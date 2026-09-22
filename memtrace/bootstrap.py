"""把 agent-Joshu 主包复制为项目自含工具包。"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import bootstrap_files as files
from . import store
from .timeutil import rfc3339_now

COMPONENT_ORDER = ("模板", "Skills", "memtrace", "OMP 扩展")


@dataclass
class ComponentStats:
    directories: int
    files: int = 0
    added: int = 0
    updated: int = 0
    conflicts: int = 0
    unchanged: int = 0


@dataclass
class BootstrapReport:
    stats: dict[str, ComponentStats]
    installed: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    residual: list[str] = field(default_factory=list)
    untouched: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)
    manifest_changed: bool = False


def kit_root() -> Path:
    """按 memtrace 包自身位置定位主包根，不依赖 cwd。"""
    return Path(__file__).resolve().parent.parent


def available_skills(root: Path) -> list[str]:
    skills_root = root / "skills"
    try:
        return sorted(
            path.name
            for path in skills_root.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file()
        )
    except OSError as exc:
        raise store.MemtraceError("主包 skills/ 目录不可读") from exc


def parse_skills(raw: str | None, valid: list[str]) -> list[str]:
    if raw is None:
        return list(valid)
    requested = sorted({name.strip() for name in raw.split(",") if name.strip()})
    if not requested:
        raise ValueError("--skills 至少要包含一个 Skill 名")
    unknown = sorted(set(requested) - set(valid))
    if unknown:
        raise ValueError(
            "--skills 含未知名字："
            + ", ".join(unknown)
            + "；有效名字："
            + ", ".join(valid)
        )
    return requested


def bootstrap_project(
    target_arg: str | Path,
    *,
    skills_arg: str | None,
    dry_run: bool,
    skip_init: bool,
    init_project: Callable[[Path], int],
    print_line: Callable[[str], None],
) -> int:
    """校验目标并执行安装或更新。"""
    root = kit_root()
    target_input = Path(target_arg).expanduser()
    target = target_input.resolve()
    _validate_target(root, target, target_input)

    valid_skills = available_skills(root)
    selected_skills = parse_skills(skills_arg, valid_skills)
    version = files.read_version(root)
    manifest_path = target / "agent-joshu" / files.MANIFEST_NAME
    previous_manifest = files.load_manifest(manifest_path)
    previous_files = files.manifest_files(previous_manifest)
    try:
        sources = files.collect_sources(root, selected_skills)
    except (OSError, UnicodeError) as exc:
        raise store.MemtraceError("读取主包 kit 内容失败，请检查源目录权限与编码") from exc

    report = BootstrapReport(
        stats={
            "模板": ComponentStats(directories=1),
            "Skills": ComponentStats(directories=len(selected_skills)),
            "memtrace": ComponentStats(directories=1),
            "OMP 扩展": ComponentStats(directories=1),
        }
    )
    for source in sources:
        report.stats[source.component].files += 1

    desired_files: dict[str, str] = {}
    active_path = "."
    try:
        for source in sources:
            active_path = source.relative
            old_digest = previous_files.get(source.relative)
            action, wrote = files.sync_file(target, source, old_digest, dry_run=dry_run)
            stats = report.stats[source.component]
            if action == "added":
                stats.added += 1
                report.installed.append(source.relative)
                desired_files[source.relative] = source.digest
                if wrote:
                    report.written.append(source.relative)
            elif action == "updated":
                stats.updated += 1
                report.updated.append(source.relative)
                desired_files[source.relative] = source.digest
                if wrote:
                    report.written.append(source.relative)
            elif action == "conflict":
                stats.conflicts += 1
                conflict_path = source.relative + ".new"
                report.conflicts.append(conflict_path)
                if old_digest is not None:
                    desired_files[source.relative] = old_digest
                if wrote:
                    report.written.append(conflict_path)
            else:
                stats.unchanged += 1
                desired_files[source.relative] = source.digest

        current_paths = {source.relative for source in sources}
        report.residual = sorted(
            relative
            for relative in previous_files
            if relative not in current_paths and (target / relative).exists()
        )
        report.untouched.extend(files.collect_project_owned(target))

        active_path = ".gitignore"
        gitignore_action = files.merge_gitignore(root, target, dry_run=dry_run)
        if gitignore_action == "changed" and not dry_run:
            report.written.append(".gitignore")
        elif gitignore_action == "unchanged":
            report.untouched.append(".gitignore")

        active_path = "AGENTS.md"
        agents_action = files.merge_agents(root, target, version, dry_run=dry_run)
        if agents_action == "changed" and not dry_run:
            report.written.append("AGENTS.md")
        elif agents_action == "unchanged":
            report.untouched.append("AGENTS.md（已有 agent-joshu 标记区块）")

        if not skip_init:
            if dry_run:
                print_line("预览：将执行 memtrace init。")
            else:
                active_path = ".agents/memtrace_config.toml"
                try:
                    init_result = init_project(target)
                except Exception as exc:
                    raise store.MemtraceError(
                        "memtrace init 失败；kit 内容已就位，可修复后重跑 bootstrap。"
                    ) from exc
                if init_result != 0:
                    raise store.MemtraceError(
                        f"memtrace init 失败（退出码 {init_result}）；kit 内容已就位，可修复后重跑 bootstrap。"
                    )

        manifest_state = {
            "schema_version": files.MANIFEST_SCHEMA_VERSION,
            "version": version,
            "skills": selected_skills,
            "files": dict(sorted(desired_files.items())),
        }
        previous_state = files.manifest_state(previous_manifest)
        kit_writes = bool(report.installed or report.updated)
        conflict_writes = (
            bool(report.conflicts)
            if dry_run
            else any(path.endswith(".new") for path in report.written)
        )
        report.manifest_changed = previous_state != manifest_state or kit_writes or conflict_writes

        if report.manifest_changed and not dry_run:
            active_path = f"agent-joshu/{files.MANIFEST_NAME}"
            manifest = dict(manifest_state)
            manifest["generated_at"] = rfc3339_now()
            files.write_manifest(manifest_path, manifest)
            report.written.append(active_path)
    except store.MemtraceError:
        raise
    except (OSError, UnicodeError) as exc:
        written = "、".join(report.written) if report.written else "无"
        raise store.MemtraceError(
            f"写入失败：{active_path}（{type(exc).__name__}）；本次已写入：{written}"
        ) from exc

    _print_report(
        report,
        selected_skills=selected_skills,
        dry_run=dry_run,
        skip_init=skip_init,
        print_line=print_line,
    )
    return 0


def _validate_target(root: Path, target: Path, target_input: Path) -> None:
    if target == root or root in target.parents:
        raise store.MemtraceError("目标项目不能是主包自身或其子目录")
    if not target.exists() or not target.is_dir():
        raise store.MemtraceError(
            f"目标路径不存在或不是目录：{_display_input_path(target_input)}"
        )
    agent_dir = target / "agent-joshu"
    if agent_dir.exists() and not (agent_dir / "VERSION").is_file():
        raise store.MemtraceError(
            "目标已有 agent-joshu/ 但缺少 VERSION，疑似项目自建目录；请先确认并删除或移走该目录"
        )


def _display_input_path(path: Path) -> str:
    try:
        relative = os.path.relpath(path.resolve(), Path.cwd().resolve())
    except (OSError, ValueError):
        return path.name or "."
    return Path(relative).as_posix()


def _print_report(
    report: BootstrapReport,
    *,
    selected_skills: list[str],
    dry_run: bool,
    skip_init: bool,
    print_line: Callable[[str], None],
) -> None:
    mode = "预览完成" if dry_run else "完成"
    print_line(f"bootstrap {mode}：目标项目根 .")
    for component in COMPONENT_ORDER:
        stats = report.stats[component]
        print_line(
            f"{component}：{stats.directories} 个目录，{stats.files} 个文件"
            f"（新增 {stats.added}，更新 {stats.updated}，冲突 {stats.conflicts}，无变化 {stats.unchanged}）"
        )
    print_line("Skills：" + ", ".join(selected_skills))
    _print_section("已更新（kit 覆盖）", report.updated, print_line)
    conflict_title = (
        "冲突预览（将写 .new）"
        if dry_run
        else "冲突保留项目版（.new 已写）"
    )
    _print_section(conflict_title, report.conflicts, print_line)
    _print_section("主包已删除（项目残留）", report.residual, print_line)
    _print_section("项目自有内容（未触碰）", sorted(set(report.untouched)), print_line)
    if report.manifest_changed:
        verb = "将更新" if dry_run else "已更新"
        print_line(f"{verb} agent-joshu/{files.MANIFEST_NAME}")
    else:
        print_line(f"agent-joshu/{files.MANIFEST_NAME} 无变化")
    if skip_init:
        print_line("已跳过 memtrace init（--skip-init）。")
    print_line("后续：重启 OMP，再按 tests/omp-loading.md 检查 Skill 与 memtrace 注入。")


def _print_section(
    title: str,
    paths: list[str],
    print_line: Callable[[str], None],
) -> None:
    print_line(f"{title}：")
    if not paths:
        print_line("  （无）")
        return
    for path in paths:
        print_line(f"  {path}")
