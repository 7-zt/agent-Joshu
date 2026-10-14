#!/usr/bin/env python3
"""summarizer 会话提取脚本。

扫描本机三家 agent（omp / claude / codex）的会话文件，按目标项目根过滤，
把「人话对话」（用户与助手的文本轮次）导出为可蒸馏的纯文本。

仅依赖标准库，Python 3.10+，Windows 兼容。

子命令：
    new   [--project PATH]          列出本项目下新增或有变更的会话（JSONL）
    show  <session_id> [--project PATH]
                                    把某会话人话对话写入临时 dump 文件，打印路径
    done  [--project PATH]          全量重写状态文件中本项目的指纹

--project 默认当前工作目录。
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1

# 会话来源目录（相对用户主目录）。缺失即该来源为空，不报错。
SOURCE_DIRS = {
    "omp": Path(".omp") / "agent" / "sessions",
    "claude": Path(".claude") / "projects",
    "codex": Path(".codex") / "sessions",
}

# 三家务话文本里混入的注入标记（slash 命令回显、环境上下文、shell 包装），整条丢弃。
NOISE_PREFIXES = (
    "<local-command-caveat>",
    "<local-command-stdout>",
    "<command-name>",
    "<command-message>",
    "<command-args>",
    "<system-reminder>",
    "<user_shell_command>",
    "<environment_context>",
    "<turn_aborted>",
    "# AGENTS.md instructions",
)


def norm(path: str | os.PathLike[str]) -> str:
    """路径规范化，用于比较（大小写不敏感）。"""
    return os.path.normcase(os.path.normpath(str(path)))


def state_path(project: Path) -> Path:
    return project / ".agents" / "summarizer-state.json"


def load_state(project: Path) -> dict:
    path = state_path(project)
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if isinstance(data, dict) and isinstance(data.get("fingerprints"), dict):
            return data
    return {"schema_version": SCHEMA_VERSION, "fingerprints": {}}


def iter_session_files(source: str) -> list[Path]:
    root = Path.home() / SOURCE_DIRS[source]
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.jsonl"))


def read_jsonl(path: Path):
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except OSError:
        return


def iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def file_started(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


def session_meta(source: str, path: Path) -> tuple[str | None, str | None]:
    """从会话文件读 (cwd, started)。只读到拿到 cwd 即止。"""
    cwd: str | None = None
    started: str | None = None
    for i, obj in enumerate(read_jsonl(path)):
        if source == "codex":
            if obj.get("type") == "session_meta":
                payload = obj.get("payload") or {}
                cwd = payload.get("cwd") or cwd
                started = iso(payload.get("timestamp")) or iso(obj.get("timestamp"))
                break
        elif source == "omp":
            if obj.get("type") == "session":
                cwd = obj.get("cwd") or cwd
                started = iso(obj.get("timestamp"))
                break
        else:  # claude：任何带 cwd 的行；started＝最早时间戳
            if obj.get("cwd"):
                cwd = obj["cwd"]
                started = started or iso(obj.get("timestamp"))
                break
        if i > 200:
            break
    return cwd, started


def session_record(source: str, path: Path, cwd: str, started: str | None) -> dict:
    stat = path.stat()
    return {
        "agent": source,
        "session_id": path.stem,
        "file": str(path),
        "started": started or file_started(path),
        "size": stat.st_size,
        "mtime": stat.st_mtime,
    }


def project_sessions(project: Path) -> list[dict]:
    target = norm(project)
    records: list[dict] = []
    for source in SOURCE_DIRS:
        for path in iter_session_files(source):
            cwd, started = session_meta(source, path)
            if cwd and norm(cwd) == target:
                records.append(session_record(source, path, cwd, started))
    records.sort(key=lambda r: (r["started"], r["agent"], r["session_id"]))
    return records


def cmd_new(project: Path) -> int:
    state = load_state(project)
    fingerprints = state.get("fingerprints", {})
    for record in project_sessions(project):
        known = fingerprints.get(record["agent"], {}).get(record["file"])
        changed = (
            not known
            or known.get("size") != record["size"]
            or known.get("mtime") != record["mtime"]
        )
        if changed:
            print(json.dumps(record, ensure_ascii=False))
    return 0


def extract_dialogue(source: str, path: Path) -> list[tuple[str, str, str]]:
    """返回 [(timestamp_iso, role, text)]，剥离工具调用/thinking/附件/sidechain。"""
    turns: list[tuple[str, str, str]] = []
    for obj in read_jsonl(path):
        ts = obj.get("timestamp")
        if source == "codex":
            if obj.get("type") != "response_item":
                continue
            payload = obj.get("payload") or {}
            if payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role not in ("user", "assistant"):
                continue
            text = _join_blocks(payload.get("content"), ("input_text", "output_text"))
            if text and not _is_noise(text):
                turns.append((ts, role, text))
        elif source == "omp":
            if obj.get("type") != "message":
                continue
            message = obj.get("message") or {}
            role = message.get("role")
            if role not in ("user", "assistant"):
                continue
            text = _join_blocks(message.get("content"), ("text",))
            if text and not _is_noise(text):
                turns.append((ts, role, text))
        else:  # claude
            if obj.get("type") not in ("user", "assistant"):
                continue
            if obj.get("isSidechain") or obj.get("isMeta"):
                continue
            role = obj.get("type")
            content = (obj.get("message") or {}).get("content")
            if isinstance(content, str):
                text = content.strip()
            elif isinstance(content, list):
                text = _join_blocks(content, ("text",))
            else:
                text = ""
            if text and not _is_noise(text):
                turns.append((ts, role, text))
    return turns


def _join_blocks(content, wanted: tuple[str, ...]) -> str:
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, dict) and block.get("type") in wanted:
            piece = block.get("text")
            if piece:
                parts.append(piece.strip())
    return "\n\n".join(p for p in parts if p)


def _is_noise(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(NOISE_PREFIXES)


def fmt_header(ts: str | None, role: str) -> str:
    if ts:
        try:
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            parsed = parsed.astimezone()
            stamp = parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            stamp = ts
    else:
        stamp = "未知时间"
    return f"=== {stamp} [{role}] ==="


def cmd_show(session_id: str, project: Path) -> int:
    match = next(
        (r for r in project_sessions(project) if r["session_id"] == session_id),
        None,
    )
    if match is None:
        print(f"未找到会话：{session_id}", file=sys.stderr)
        return 1
    turns = extract_dialogue(match["agent"], Path(match["file"]))
    dump_dir = Path(tempfile.gettempdir()) / "summarizer-dump"
    dump_dir.mkdir(parents=True, exist_ok=True)
    dump = dump_dir / f"{session_id}.txt"
    chunks = [
        f"# {match['agent']} 会话 {session_id}",
        f"# 来源：{match['file']}",
        f"# 起点：{match['started']}",
        "",
    ]
    for ts, role, text in turns:
        chunks.append(fmt_header(ts, role))
        chunks.append(text)
        chunks.append("")
    dump.write_text("\n".join(chunks), encoding="utf-8", newline="\n")
    print(str(dump))
    return 0


def cmd_done(project: Path) -> int:
    fingerprints: dict[str, dict] = {source: {} for source in SOURCE_DIRS}
    for record in project_sessions(project):
        fingerprints[record["agent"]][record["file"]] = {
            "size": record["size"],
            "mtime": record["mtime"],
        }
    state = {"schema_version": SCHEMA_VERSION, "fingerprints": fingerprints}
    path = state_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    total = sum(len(v) for v in fingerprints.values())
    print(f"已提交 {total} 个会话指纹到 {path}")
    return 0


def parse_project(argv: list[str]) -> tuple[Path, list[str]]:
    rest: list[str] = []
    project = Path.cwd()
    i = 0
    while i < len(argv):
        if argv[i] == "--project":
            if i + 1 >= len(argv):
                raise ValueError("--project 缺少路径参数")
            project = Path(argv[i + 1])
            i += 2
        elif argv[i].startswith("--project="):
            project = Path(argv[i].split("=", 1)[1])
            i += 1
        else:
            rest.append(argv[i])
            i += 1
    return project, rest


def main(argv: list[str]) -> int:
    if not argv:
        print("用法：extract.py {new|show|done} [--project PATH]", file=sys.stderr)
        return 2
    command = argv[0]
    try:
        project, rest = parse_project(argv[1:])
    except ValueError as error:
        print(f"参数错误：{error}", file=sys.stderr)
        return 2
    project = project.resolve()
    if command == "new":
        return cmd_new(project)
    if command == "done":
        return cmd_done(project)
    if command == "show":
        if not rest:
            print("show 需要提供 session_id", file=sys.stderr)
            return 2
        return cmd_show(rest[0], project)
    print(f"未知子命令：{command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
