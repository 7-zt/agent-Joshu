"""memtrace CLI：init / bootstrap / create / log / read / search / update。

零第三方依赖，argparse 子命令。Windows 与 Linux 均可运行
（Python 3.10+，路径全用 pathlib，文本统一 UTF-8 + LF）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from . import bootstrap as bootstrap_mod
from . import config as config_mod
from . import search as search_mod
from . import store, wal


def _print(text: str) -> None:
    sys.stdout.write(text + "\n")


def _relative_display(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def init_project(root: Path) -> int:
    root = root.resolve()
    path = config_mod.config_path(root)
    if path.is_file():
        _print(f"已存在：{_relative_display(path, root)}（幂等，不覆盖）")
        return 0
    config_mod.write_config(root)
    task_root = config_mod.task_root_dir(root)
    task_root.mkdir(parents=True, exist_ok=True)
    _print(f"已写入 {_relative_display(path, root)}")
    _print(f"已创建任务根目录 {_relative_display(task_root, root)}/")
    git_policy = str(config_mod.load_config(root).get("git_policy", config_mod.DEFAULT_GIT_POLICY))
    if git_policy == "track":
        _print("git_policy=track：任务过程将进项目 git；请勿将 .memtrace/ 加入 .gitignore。")
    elif git_policy == "none":
        _print("git_policy=none：不管理 git 策略，.memtrace/ 是否忽略由你自行决定。")
    else:
        _print(
            "任务过程目录 .memtrace/ 按默认策略留在本地（git_policy=ignore）；"
            "bootstrap 已代为追加 .gitignore 时无需手动处理，手动 init 的项目请自行加入 .gitignore。"
        )
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    return init_project(Path.cwd())


def cmd_bootstrap(args: argparse.Namespace) -> int:
    return bootstrap_mod.bootstrap_project(
        args.target,
        skills_arg=args.skills,
        dry_run=args.dry_run,
        skip_init=args.skip_init,
        init_project=init_project,
        print_line=_print,
    )


def cmd_create(args: argparse.Namespace) -> int:
    project_root, cfg = store.require_project(Path.cwd())
    task = store.create_task(
        project_root,
        cfg,
        name=args.name,
        body=args.body,
        status=args.status,
        creation_policy="permissive" if args.permissive else None,
    )
    _print(store.render_task_summary(task, project_root, cfg))
    _print(f"任务已创建。下一步：编辑 TASK.md，用 memtrace log 记第一条 WAL。")
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    project_root, cfg = store.require_project(Path.cwd())
    task = store.find_task(project_root, cfg, args.task)
    body = wal.semantic_body(
        changes=args.changes,
        reversals=args.reversals,
        verification=args.verification,
        user_correction=args.user_correction,
    )
    if args.body and args.body.strip():
        body = (body + "\n\n" + args.body.strip()).strip()
    path = wal.append_entry(task.dir, args.actor, args.message, body=body or None)
    rel = path.relative_to(project_root).as_posix() if _is_relative(path, project_root) else str(path)
    _print(f"已追加 1 条（actor={args.actor}）→ {rel}")
    return 0


def _is_relative(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def cmd_read(args: argparse.Namespace) -> int:
    project_root, cfg = store.require_project(Path.cwd())
    if args.list:
        tasks = store.load_tasks(project_root, cfg)
        if not tasks:
            _print("（无任务）")
            return 0
        for task in tasks:
            _print(store.render_task_summary(task, project_root, cfg) + "\n")
        return 0
    task = store.find_task(project_root, cfg, args.task)
    _print(store.render_task_summary(task, project_root, cfg))
    task_md = task.dir / "TASK.md"
    if task_md.is_file():
        text = task_md.read_text(encoding="utf-8")
        if args.full:
            _print("\n----- TASK.md -----")
            _print(text.rstrip())
        else:
            head = "\n".join(text.splitlines()[: int(args.head)])
            _print("\n----- TASK.md（前 {} 行）-----".format(int(args.head)))
            _print(head)
            _print("（memtrace read <任务> --full 看全文）")
    if args.wal:
        entries = wal.parse_all_entries(task.dir)
        _print(f"\n----- WAL（{len(entries)} 条）-----")
        for entry in entries:
            _print(f"## {entry['timestamp']} · {entry['actor']}")
            raw = entry["raw"]
            if raw:
                shown = raw if args.full else "\n".join(raw.splitlines()[:8])
                _print(shown)
            _print("")
    else:
        wal_files = wal.list_wal_files(task.dir)
        _print(f"\n----- WAL 文件 {len(wal_files)} 个（--wal 看内容）-----")
        for path in wal_files:
            _print("  " + path.relative_to(task.dir).as_posix())
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    project_root, cfg = store.require_project(Path.cwd())
    try:
        hits = search_mod.search_project(
            project_root,
            cfg,
            args.pattern,
            regex=args.regex,
            ignore_case=not args.case_sensitive,
            context=args.context,
            max_hits=args.max_hits,
        )
    except ValueError as exc:
        _print(f"错误：{exc}")
        return 2
    if not hits:
        _print(f"（无命中：{args.pattern}）")
        return 0
    for hit in hits:
        location = f"{hit['path']}:{hit['line']}"
        if hit["task"]:
            _print(f"[{hit['task']}] {location}")
        else:
            _print(location)
        _print(f"  {hit['text']}")
        if hit["context"] and args.context:
            _print("  | " + hit["context"].replace("\n", "\n  | "))
    _print(f"\n共 {len(hits)} 处命中。")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    project_root, cfg = store.require_project(Path.cwd())
    task = store.find_task(project_root, cfg, args.task)
    new_status = args.status
    reason = args.reason
    updated = store.update_status(project_root, cfg, task, new_status, reason)
    wal_body = None
    if new_status == "closed":
        wal_body = f"### 变更\n\n任务关闭。原因：{reason.strip()}"
    elif reason and reason.strip():
        wal_body = f"### 用户纠正\n\n{reason.strip()}"
    if wal_body:
        wal.append_entry(task.dir, args.actor, f"状态转换：{task.status} → {new_status}", body=wal_body)
    _print(store.render_task_summary(updated, project_root, cfg))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="memtrace",
        description="结构化任务过程记录器（含任务管理）。规格见 grill-memtrace.md v1.0。",
    )
    parser.add_argument("--version", action="version", version=f"memtrace {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="在项目根初始化（写 .agents/memtrace_config.toml + 任务根目录）")
    p_init.set_defaults(func=cmd_init)

    p_bootstrap = sub.add_parser("bootstrap", help="把主包复制为目标项目内的自含工具包")
    p_bootstrap.add_argument("target", help="已存在的目标项目路径")
    p_bootstrap.add_argument("--skills", help="逗号分隔的 Skill 子集；缺省复制全部")
    p_bootstrap.add_argument("--dry-run", action="store_true", help="只预览动作与漂移，不写文件")
    p_bootstrap.add_argument("--skip-init", action="store_true", help="跳过收尾 memtrace init")
    p_bootstrap.set_defaults(func=cmd_bootstrap)

    p_create = sub.add_parser("create", help="创建任务（目录 + memtrace.toml + TASK.md）")
    p_create.add_argument("name", help="任务名（生成目录短名 slug）")
    p_create.add_argument("--body", help="TASK.md 初始正文（缺省用模板）")
    p_create.add_argument("--status", choices=store.STATUSES, default="planning")
    p_create.add_argument("--permissive", action="store_true", help="跳过 strict 的未关闭任务检查")
    p_create.set_defaults(func=cmd_create)

    p_log = sub.add_parser("log", help="追加 WAL 条目（阶段性汇总；含语义小节）")
    p_log.add_argument("task", help="任务引用（目录名 / id 前缀）")
    p_log.add_argument("message", help="一句话消息")
    p_log.add_argument("--actor", default="agent", help="记录者（如 mt-impl、memtrace-hook、user）")
    p_log.add_argument("--changes", help="变更小节：文件 + 为什么")
    p_log.add_argument("--reversals", help="推翻小节：旧→新 + 为什么")
    p_log.add_argument("--verification", help="验证小节：跑了什么 + 结果")
    p_log.add_argument("--user-correction", help="用户纠正小节")
    p_log.add_argument("--body", help="自由正文（附在语义小节后）")
    p_log.set_defaults(func=cmd_log)

    p_read = sub.add_parser("read", help="读任务元数据 / TASK.md / WAL")
    p_read.add_argument("task", nargs="?", help="任务引用；--list 时省略")
    p_read.add_argument("--list", action="store_true", help="列出全部任务")
    p_read.add_argument("--full", action="store_true", help="TASK.md 全文 / WAL 条目全文")
    p_read.add_argument("--head", default="30", help="TASK.md 预览行数（默认 30）")
    p_read.add_argument("--wal", action="store_true", help="附 WAL 条目")
    p_read.set_defaults(func=cmd_read)

    p_search = sub.add_parser("search", help="跨任务全文检索")
    p_search.add_argument("pattern", help="搜索词（--regex 开正则）")
    p_search.add_argument("--regex", action="store_true")
    p_search.add_argument("-i", "--case-sensitive", action="store_true")
    p_search.add_argument("-C", "--context", type=int, default=0, help="上下文行数")
    p_search.add_argument("--max-hits", type=int, default=200)
    p_search.set_defaults(func=cmd_search)

    p_update = sub.add_parser("update", help="状态转换（planning/open/closed）")
    p_update.add_argument("task", help="任务引用")
    p_update.add_argument("--status", choices=store.STATUSES, required=True)
    p_update.add_argument("--reason", help="关闭必填原因；其他状态可选记入用户纠正")
    p_update.add_argument("--actor", default="agent")
    p_update.set_defaults(func=cmd_update)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except store.MemtraceError as exc:
        sys.stderr.write(f"错误：{exc}\n")
        return 1
    except ValueError as exc:
        sys.stderr.write(f"错误：{exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
