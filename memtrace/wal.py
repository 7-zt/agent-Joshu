"""WAL：wal/YYYY-MM-DD.md 追加式 Markdown。

条目格式（tk 同款）：

    ## <RFC3339 时间戳> · <actor>

    <消息>

    <可选正文>

语义小节（AI 阶段性写入时遵守）：变更（文件+为什么）、推翻（旧→新+为什么）、
验证（跑了什么+结果）、用户纠正。
"""

from __future__ import annotations

from pathlib import Path

from .store import WAL_SEMANTIC_SECTIONS
from .timeutil import rfc3339_now, today_local


def wal_dir(task_dir: Path) -> Path:
    return task_dir / "wal"


def wal_path(task_dir: Path, date: str | None = None) -> Path:
    return wal_dir(task_dir) / f"{date or today_local()}.md"


def append_entry(
    task_dir: Path,
    actor: str,
    message: str,
    body: str | None = None,
    timestamp: str | None = None,
) -> Path:
    """追加一条 WAL 条目（文件不存在则带标题创建）。返回 WAL 文件路径。"""
    if not actor.strip():
        raise ValueError("actor 不能为空")
    if not message.strip():
        raise ValueError("message 不能为空")
    path = wal_path(task_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = timestamp or rfc3339_now()
    entry = f"## {ts} · {actor.strip()}\n\n{message.strip()}\n"
    if body and body.strip():
        entry += f"\n{body.strip()}\n"
    is_new = not path.exists()
    if is_new:
        header = f"# WAL {path.stem}\n\n"
        content = header + entry
    else:
        content = entry
    # WAL 是追加式日志，直接追加写（非原子替换），与「不参与事务」语义一致
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    return path


def read_wal(task_dir: Path, date: str | None = None) -> str:
    path = wal_path(task_dir, date)
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def list_wal_files(task_dir: Path) -> list[Path]:
    directory = wal_dir(task_dir)
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.iterdir() if p.is_file() and p.suffix == ".md")


def recent_wal(task_dir: Path, max_entries: int = 5) -> str:
    """跨全部 WAL 文件取最后 max_entries 条，按时间序拼接（注入摘要用）。"""
    entries = parse_all_entries(task_dir)
    tail = entries[-max_entries:]
    if not tail:
        return ""
    parts = []
    for entry in tail:
        head = f"## {entry['timestamp']} · {entry['actor']}"
        parts.append(head + ("\n" + entry["raw"].strip() if entry["raw"].strip() else ""))
    return "\n\n".join(parts)


_ENTRY_RE_PREFIX = "## "


def parse_all_entries(task_dir: Path) -> list[dict]:
    """解析全部 WAL 文件为条目列表（timestamp/actor/raw 正文）。"""
    entries: list[dict] = []
    for path in list_wal_files(task_dir):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        current: dict | None = None
        body_lines: list[str] = []
        for line in lines:
            if line.startswith(_ENTRY_RE_PREFIX) and " · " in line:
                if current is not None:
                    current["raw"] = "\n".join(body_lines).strip()
                    entries.append(current)
                head = line[len(_ENTRY_RE_PREFIX) :].strip()
                timestamp, _, actor = head.partition(" · ")
                current = {"timestamp": timestamp.strip(), "actor": actor.strip(), "raw": ""}
                body_lines = []
            elif current is not None:
                body_lines.append(line)
        if current is not None:
            current["raw"] = "\n".join(body_lines).strip()
            entries.append(current)
    return entries


def semantic_body(changes: str | None = None, reversals: str | None = None,
                  verification: str | None = None, user_correction: str | None = None) -> str:
    """按语义小节拼正文；只输出给了内容的小节。"""
    sections = [
        ("变更", changes),
        ("推翻", reversals),
        ("验证", verification),
        ("用户纠正", user_correction),
    ]
    parts = [f"### {title}\n\n{content.strip()}" for title, content in sections if content and content.strip()]
    return "\n\n".join(parts)


def semantic_section_titles() -> tuple[str, ...]:
    return WAL_SEMANTIC_SECTIONS
