"""任务存储：目录扫描、memtrace.toml 读写、任务创建与状态转换。

数据模型（tk schema v1，split 模式）：
- 任务目录 <task_root>/YYYY/MM/DD-NN--slug/
- memtrace.toml 七字段：schema_version/id/name/status/created_at/depends_on/related_to
  （extra 为可选第八键）
- 正文 TASK.md
- WAL wal/YYYY-MM-DD.md（见 wal.py）
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from . import config as config_mod
from . import uuid7
from .timeutil import rfc3339_now, today_parts

SCHEMA_VERSION = 1
STATUSES = ("planning", "open", "closed")

# 目录名：DD-NN--slug；旧实现生成的 YYYY-MM-DD-NN--slug 仍可扫描。
TASK_DIR_RE = re.compile(r"^(\d{2})-(\d{2})--(.+)$")
LEGACY_TASK_DIR_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(\d{2})--(.+)$")

WAL_SEMANTIC_SECTIONS = ("变更", "推翻", "验证", "用户纠正")


class MemtraceError(Exception):
    """memtrace 业务错误（带用户可读信息）。"""


class Task:
    def __init__(self, dir_path: Path, meta: dict):
        self.dir = dir_path
        self.meta = meta

    @property
    def id(self) -> str:
        return str(self.meta["id"])

    @property
    def name(self) -> str:
        return str(self.meta["name"])

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "planning"))

    @property
    def created_at(self) -> str:
        return str(self.meta.get("created_at", ""))

    def relative(self, project_root: Path) -> str:
        try:
            return self.dir.relative_to(project_root).as_posix()
        except ValueError:
            return str(self.dir)


# ---------------------------------------------------------------------------
# memtrace.toml 序列化（保留手工编辑的未知键；顺序稳定）
# ---------------------------------------------------------------------------

_META_KEY_ORDER = [
    "schema_version",
    "id",
    "name",
    "status",
    "created_at",
    "depends_on",
    "related_to",
    "extra",
]


def _format_toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(_format_toml_value(v) for v in value) + "]"
    # 字符串：含双引号时用单引号字面量，否则双引号
    text = str(value)
    if '"' in text and "'" not in text:
        return f"'{text}'"
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def dump_meta(meta: dict) -> str:
    lines = ["# memtrace 任务元数据（schema v1；生成后可手工补 depends_on/related_to/extra）", ""]
    emitted = set()
    for key in _META_KEY_ORDER:
        if key not in meta:
            continue
        emitted.add(key)
        lines.append(f"{key} = {_format_toml_value(meta[key])}")
    for key, value in meta.items():  # 保留未知键
        if key not in emitted:
            lines.append(f"{key} = {_format_toml_value(value)}")
    lines.append("")
    return "\n".join(lines)


def parse_task_toml(text: str) -> dict:
    """解析任务元数据 TOML（顶层键值子集 + [extra] 表）。"""
    meta: dict = {}
    in_extra = False
    for raw_line in text.lstrip("\ufeff").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            in_extra = line == "[extra]"
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        value = _parse_toml_value(raw_value)
        if in_extra:
            extra = meta.setdefault("extra", {})
            if isinstance(extra, dict):
                extra[key] = value
        elif key:
            meta[key] = value
    return meta


def _parse_toml_value(raw: str):
    from .config import _parse_scalar  # 同一子集解析

    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        # 按逗号切顶层（v1 不支持嵌套数组/字符串内逗号含引号转义以外的复杂形）
        parts, buf, quote = [], "", None
        for ch in inner:
            if quote:
                buf += ch
                if ch == quote:
                    quote = None
                continue
            if ch in ("'", '"'):
                quote = ch
                buf += ch
                continue
            if ch == ",":
                parts.append(buf)
                buf = ""
                continue
            buf += ch
        if buf.strip():
            parts.append(buf)
        return [_parse_scalar(p) for p in parts if p.strip()]
    return _parse_scalar(value)


# ---------------------------------------------------------------------------
# 目录扫描与任务解析
# ---------------------------------------------------------------------------


def find_project_root(start: Path) -> Path | None:
    """向上找含 .agents/memtrace_config.toml 或 task_root 标记的目录。"""
    current = start.resolve()
    while True:
        if config_mod.config_path(current).is_file():
            return current
        # 无配置文件时，存在 .memtrace/ 目录也算已 init
        if (current / config_mod.DEFAULT_TASK_ROOT).is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def require_project(start: Path) -> tuple[Path, dict]:
    root = find_project_root(start)
    if root is None:
        raise MemtraceError(
            "未找到 memtrace 项目（向上未探测到 .agents/memtrace_config.toml 或 .memtrace/）。先在项目根执行 memtrace init。"
        )
    cfg = config_mod.load_config(root)
    errors = config_mod.validate_config(cfg)
    if errors:
        raise MemtraceError("配置无效：" + "；".join(errors))
    return root, cfg


def _load_task(task_dir: Path) -> Task | None:
    meta_path = task_dir / "memtrace.toml"
    if not meta_path.is_file():
        return None
    meta = parse_task_toml(meta_path.read_text(encoding="utf-8"))
    if not meta:
        return None
    _validate_meta(meta, meta_path)
    return Task(task_dir, meta)


def _validate_meta(meta: dict, source: Path) -> None:
    required = {
        "schema_version",
        "id",
        "name",
        "status",
        "created_at",
        "depends_on",
        "related_to",
    }
    missing = sorted(required - meta.keys())
    if missing:
        raise MemtraceError(f"任务元数据缺少字段（{source}）：{', '.join(missing)}")
    if meta["schema_version"] != SCHEMA_VERSION:
        raise MemtraceError(
            f"不支持的 schema_version（{source}）：{meta['schema_version']}，当前支持 {SCHEMA_VERSION}"
        )
    if meta["status"] not in STATUSES:
        raise MemtraceError(f"任务状态无效（{source}）：{meta['status']}")
    for key in ("depends_on", "related_to"):
        if not isinstance(meta[key], list):
            raise MemtraceError(f"任务元数据字段必须是数组（{source}）：{key}")


def load_tasks(project_root: Path, cfg: dict) -> list[Task]:
    """全量扫描 task_root 下的任务目录（含子任务目录不递归为独立任务）。"""
    root_dir = config_mod.task_root_dir(project_root, cfg)
    tasks: list[Task] = []
    if not root_dir.is_dir():
        return tasks
    for year_dir in _sorted_dirs(root_dir):
        for month_dir in _sorted_dirs(year_dir):
            for task_dir in _sorted_dirs(month_dir):
                task = _load_task(task_dir)
                if task is not None:
                    tasks.append(task)
    return tasks


def _sorted_dirs(path: Path) -> list[Path]:
    try:
        return sorted(p for p in path.iterdir() if p.is_dir())
    except OSError:
        return []


def find_task(project_root: Path, cfg: dict, ref: str) -> Task:
    """按引用定位任务：目录名（含/不含日期路径）、id 前缀、序号（当日）。"""
    tasks = load_tasks(project_root, cfg)
    ref = ref.strip().strip("/")

    # 1) 目录名精确/前缀匹配（DD-NN--slug 或完整 YYYY/MM/DD-NN--slug）
    by_dir: list[Task] = []
    for task in tasks:
        dirname = task.dir.name
        rel_posix = task.dir.relative_to(config_mod.task_root_dir(project_root, cfg)).as_posix()
        if (
            ref == dirname
            or ref == rel_posix
            or dirname.startswith(ref + "--")
            or dirname.endswith("--" + ref)
        ):
            by_dir.append(task)
    if len(by_dir) == 1:
        return by_dir[0]
    if len(by_dir) > 1:
        raise MemtraceError(f"引用歧义，匹配到多个任务目录：{', '.join(t.dir.name for t in by_dir)}")

    # 2) id 前缀匹配
    by_id = [t for t in tasks if t.id.startswith(ref)]
    if len(by_id) == 1:
        return by_id[0]
    if len(by_id) > 1:
        raise MemtraceError(f"id 前缀歧义，匹配多个：{', '.join(t.id for t in by_id)}")

    raise MemtraceError(f"未找到任务：{ref}（可用 memtrace read --list 查看全部任务）")


def _next_seq_for_date(root_dir: Path, year: str, month: str, date: str) -> int:
    """给定日期的下一个序号：兼容旧目录并生成 DD-NN--slug。"""
    month_dir = root_dir / year / month
    max_seq = 0
    if month_dir.is_dir():
        for entry in month_dir.iterdir():
            if not entry.is_dir():
                continue
            match = TASK_DIR_RE.match(entry.name)
            if match and match.group(1) == date[-2:]:
                max_seq = max(max_seq, int(match.group(2)))
                continue
            legacy = LEGACY_TASK_DIR_RE.match(entry.name)
            if legacy and legacy.group(1) == date:
                max_seq = max(max_seq, int(legacy.group(2)))
    return max_seq + 1


_SLUG_RE = re.compile(r"[^0-9A-Za-z一-鿿]+")


def make_slug(name: str, max_len: int = 48) -> str:
    """短名：保留中英文与数字，其余折叠为单个连字符。"""
    slug = _SLUG_RE.sub("-", name.strip()).strip("-")
    # 控制长度（按字符）
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug or "task"


def create_task(
    project_root: Path,
    cfg: dict,
    name: str,
    body: str | None = None,
    status: str = "planning",
    creation_policy: str | None = None,
) -> Task:
    if status not in STATUSES:
        raise MemtraceError(f"status 必须是 {'/'.join(STATUSES)}")
    root_dir = config_mod.task_root_dir(project_root, cfg)
    year, month, day = today_parts()
    date = f"{year}-{month}-{day}"

    open_statuses = {"planning", "open"}
    policy = creation_policy or str(cfg.get("creation_policy", "strict"))
    if policy == "strict":
        existing = load_tasks(project_root, cfg)
        active = [t for t in existing if t.status in open_statuses]
        if active:
            names = ", ".join(f"{t.dir.name}（{t.status}）" for t in active)
            raise MemtraceError(
                f"strict 模式：存在未关闭任务，先关闭或换 permissive。\n活跃任务：{names}"
            )

    seq = _next_seq_for_date(root_dir, year, month, date)
    slug = make_slug(name)
    task_dir = root_dir / year / month / f"{day}-{seq:02d}--{slug}"
    if task_dir.exists():
        raise MemtraceError(f"任务目录已存在：{task_dir}")
    task_dir.mkdir(parents=True)

    meta = {
        "schema_version": SCHEMA_VERSION,
        "id": uuid7.uuid7(),
        "name": name,
        "status": status,
        "created_at": rfc3339_now(),
        "depends_on": [],
        "related_to": [],
    }
    _atomic_write(task_dir / "memtrace.toml", dump_meta(meta))

    task_body = body if body is not None else f"# {name}\n\n## 目标\n\n## 材料入口\n"
    _atomic_write(task_dir / "TASK.md", task_body.rstrip() + "\n")

    return Task(task_dir, meta)


def update_status(project_root: Path, cfg: dict, task: Task, new_status: str, reason: str | None) -> Task:
    if new_status not in STATUSES:
        raise MemtraceError(f"status 必须是 {'/'.join(STATUSES)}")
    if new_status == task.status:
        raise MemtraceError(f"任务已是 {new_status}，无需转换")
    allowed = {
        "planning": {"open"},
        "open": {"closed"},
        "closed": set(),
    }
    if new_status not in allowed[task.status]:
        if task.status == "closed":
            raise MemtraceError("closed 是终态；如需重开请手工编辑 memtrace.toml 并在 WAL 记录原因")
        raise MemtraceError(f"不允许状态转换：{task.status} → {new_status}（只能按 planning → open → closed）")
    if new_status == "closed" and not (reason and reason.strip()):
        raise MemtraceError("关闭任务必须给原因（--reason）")

    meta = dict(task.meta)
    meta["status"] = new_status
    _atomic_write(task.dir / "memtrace.toml", dump_meta(meta))
    return Task(task.dir, meta)


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def render_task_summary(task: Task, project_root: Path, cfg: dict) -> str:
    rel = task.relative(project_root)
    deps = task.meta.get("depends_on") or []
    lines = [
        f"{task.dir.name}",
        f"  id: {task.id}",
        f"  name: {task.name}",
        f"  status: {task.status}",
        f"  created_at: {task.created_at}",
        f"  path: {rel}",
    ]
    if deps:
        lines.append(f"  depends_on: {', '.join(str(d) for d in deps)}")
    return "\n".join(lines)
