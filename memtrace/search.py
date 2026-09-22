"""检索：跨任务的文本搜索（TASK.md、memtrace.toml、WAL、材料 Markdown）。"""

from __future__ import annotations

import re
from pathlib import Path

from . import config as config_mod

_SEARCH_SUFFIXES = {".md", ".toml", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".py", ".ts"}


def search_project(
    project_root: Path,
    cfg: dict,
    pattern: str,
    *,
    regex: bool = False,
    ignore_case: bool = True,
    context: int = 0,
    max_hits: int = 200,
) -> list[dict]:
    """在 task_root 全部任务文件中搜 pattern，返回命中列表。"""
    root_dir = config_mod.task_root_dir(project_root, cfg)
    if not root_dir.is_dir():
        return []
    if regex:
        try:
            matcher = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
        except re.error as exc:
            raise ValueError(f"正则无效：{exc}") from exc
    else:
        flags = re.IGNORECASE if ignore_case else 0
        matcher = re.compile(re.escape(pattern), flags)

    hits: list[dict] = []
    for path in _iter_files(root_dir):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = path.relative_to(root_dir).as_posix()
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            if matcher.search(line):
                ctx_start = max(0, line_no - 1 - context)
                ctx_end = min(len(lines), line_no + context)
                hits.append({
                    "path": rel,
                    "line": line_no,
                    "text": line.strip()[:400],
                    "context": "\n".join(lines[ctx_start:ctx_end]) if context else "",
                    # 任务目录 = 路径前三段 YYYY/MM/DD-NN--slug
                    "task": _task_of(rel),
                })
                if len(hits) >= max_hits:
                    return hits
    return hits


def _iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in _SEARCH_SUFFIXES:
            yield path


def _task_of(rel_posix: str) -> str:
    parts = rel_posix.split("/")
    if len(parts) >= 4:
        return "/".join(parts[:3])
    if parts:
        return parts[0]
    return ""
