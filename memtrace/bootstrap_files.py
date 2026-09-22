"""bootstrap 的文件同步、manifest 与项目内容合并。"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import store

MANIFEST_NAME = "bootstrap-manifest.json"
MANIFEST_SCHEMA_VERSION = 1
HASH_LENGTH = 16
AGENTS_MARKER_PREFIX = "<!-- agent-joshu:agents-rules v"
AGENTS_MARKER_END = "<!-- /agent-joshu:agents-rules -->"
GITIGNORE_MARKER = "# 追加到项目 .gitignore 的内容"
ADR_LIFECYCLES = {"proposal", "decision", "rejected", "archived"}


@dataclass(frozen=True)
class SourceFile:
    component: str
    source: Path
    relative: str
    digest: str


def read_version(root: Path) -> str:
    path = root / "template" / "agent-joshu" / "VERSION"
    try:
        version = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise store.MemtraceError("主包模板缺少可读的 template/agent-joshu/VERSION") from exc
    if not version:
        raise store.MemtraceError("主包 template/agent-joshu/VERSION 为空")
    return version


def collect_sources(root: Path, selected_skills: list[str]) -> list[SourceFile]:
    groups: list[tuple[str, Path, Path]] = [
        ("模板", root / "template" / "agent-joshu", Path("agent-joshu")),
        ("memtrace", root / "memtrace", Path("agent-joshu") / "memtrace"),
        (
            "OMP 扩展",
            root / ".omp" / "extensions" / "memtrace",
            Path(".omp") / "extensions" / "memtrace",
        ),
    ]
    groups.extend(
        ("Skills", root / "skills" / name, Path(".omp") / "skills" / name)
        for name in selected_skills
    )

    files: list[SourceFile] = []
    for component, source_root, destination_root in groups:
        if not source_root.is_dir():
            raise store.MemtraceError(f"主包源目录缺失：{destination_root.as_posix()}")
        for source in sorted(source_root.rglob("*")):
            relative_source = source.relative_to(source_root)
            if not source.is_file() or _ignored_source(relative_source):
                continue
            destination = destination_root / relative_source
            if component == "模板" and _project_owned_template_path(destination):
                continue
            digest = file_digest(source)
            if digest is None:
                continue
            files.append(
                SourceFile(
                    component=component,
                    source=source,
                    relative=destination.as_posix(),
                    digest=digest,
                )
            )
    return sorted(files, key=lambda item: item.relative)


def sync_file(
    target: Path,
    source: SourceFile,
    old_digest: str | None,
    *,
    dry_run: bool,
) -> tuple[str, bool]:
    destination = target / source.relative
    if not destination.exists():
        if not dry_run:
            _atomic_copy(source.source, destination)
        return "added", not dry_run
    if destination.is_file():
        current_digest = file_digest(destination)
        if current_digest == source.digest:
            return "unchanged", False
        if (
            old_digest is not None and current_digest == old_digest
        ) or (
            old_digest is None and source.relative == "agent-joshu/VERSION"
        ):
            if not dry_run:
                _atomic_copy(source.source, destination)
            return "updated", not dry_run

    candidate = destination.with_name(destination.name + ".new")
    candidate_changed = not candidate.is_file() or file_digest(candidate) != source.digest
    if not dry_run and candidate_changed:
        _atomic_copy(source.source, candidate)
    return "conflict", candidate_changed and not dry_run


def merge_gitignore(root: Path, target: Path, *, dry_run: bool) -> str:
    source = (root / "template" / "gitignore.additions").read_text(encoding="utf-8")
    destination = target / ".gitignore"
    if destination.is_file():
        current = destination.read_text(encoding="utf-8")
        current_lines = set(current.splitlines())
        wanted_lines = {line for line in source.splitlines() if line}
        if GITIGNORE_MARKER in current or wanted_lines.issubset(current_lines):
            return "unchanged"
    if not dry_run:
        _append_text_block(destination, source)
    return "changed"


def merge_agents(root: Path, target: Path, version: str, *, dry_run: bool) -> str:
    rules = (root / "template" / "agents-rules.md").read_text(encoding="utf-8")
    destination = target / "AGENTS.md"
    if destination.is_file():
        current = destination.read_text(encoding="utf-8")
        if AGENTS_MARKER_PREFIX in current:
            return "unchanged"
    start = f"{AGENTS_MARKER_PREFIX}{version} -->"
    block = f"{start}\n{rules.rstrip()}\n{AGENTS_MARKER_END}\n"
    if not dry_run:
        _append_text_block(destination, block)
    return "changed"


def load_manifest(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise store.MemtraceError(
            f"无法读取 agent-joshu/{MANIFEST_NAME}，请先修复该文件"
        ) from exc
    if not isinstance(data, dict):
        raise store.MemtraceError(
            f"agent-joshu/{MANIFEST_NAME} 顶层必须是 JSON 对象"
        )
    return data


def manifest_files(manifest: dict) -> dict[str, str]:
    raw = manifest.get("files", {})
    if not isinstance(raw, dict):
        return {}
    return {
        str(path): str(digest)
        for path, digest in raw.items()
        if isinstance(path, str) and isinstance(digest, str)
    }


def manifest_state(manifest: dict) -> dict:
    if not manifest:
        return {}
    skills = manifest.get("skills", [])
    return {
        "schema_version": manifest.get("schema_version"),
        "version": manifest.get("version"),
        "skills": sorted(str(name) for name in skills) if isinstance(skills, list) else [],
        "files": dict(sorted(manifest_files(manifest).items())),
    }


def dump_manifest(manifest: dict) -> str:
    return json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def write_manifest(path: Path, manifest: dict) -> None:
    _atomic_write_bytes(path, dump_manifest(manifest).encode("utf-8"))


def collect_project_owned(target: Path) -> list[str]:
    paths: set[str] = set()
    agent_root = target / "agent-joshu"
    for lifecycle in sorted(ADR_LIFECYCLES):
        root = agent_root / "adr" / lifecycle
        if root.is_dir():
            for path in root.rglob("*"):
                if path.is_file() and path.name != ".gitkeep":
                    paths.add(path.relative_to(target).as_posix())
    reports = agent_root / "reports"
    if reports.is_dir():
        paths.add("agent-joshu/reports/")
    config = target / ".agents" / "memtrace_config.toml"
    if config.is_file():
        paths.add(".agents/memtrace_config.toml")
    task_root = target / ".memtrace"
    if task_root.is_dir():
        paths.add(".memtrace/")
    return sorted(paths)


def file_digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:HASH_LENGTH]


def _ignored_source(relative: Path) -> bool:
    return (
        "__pycache__" in relative.parts
        or relative.suffix == ".pyc"
        or relative.name.endswith(".tmp")
    )


def _project_owned_template_path(relative: Path) -> bool:
    parts = relative.parts
    if len(parts) >= 3 and parts[:2] == ("agent-joshu", "reports"):
        return True
    if len(parts) >= 4 and parts[1] == "adr" and parts[2] in ADR_LIFECYCLES:
        return parts[-1] != ".gitkeep"
    return False


def _append_text_block(path: Path, block: str) -> None:
    existing = path.read_bytes() if path.is_file() else b""
    separator = b""
    if existing:
        separator = b"\n" if existing.endswith(b"\n") else b"\n\n"
    content = existing + separator + block.rstrip().encode("utf-8") + b"\n"
    _atomic_write_bytes(path, content)


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        shutil.copyfile(source, tmp)
        os.replace(tmp, destination)
    finally:
        if tmp.exists():
            tmp.unlink()


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        tmp = Path(tmp_name)
        if tmp.exists():
            tmp.unlink()
