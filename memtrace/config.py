"""项目配置：.agents/memtrace_config.toml（稀疏 TOML）。

零第三方依赖，手写极简 TOML 子集解析：顶层键值、字符串/bool/整数。
task_root 默认 .memtrace。
"""

from __future__ import annotations

import os
from pathlib import Path

CONFIG_DIR = ".agents"
CONFIG_NAME = "memtrace_config.toml"
DEFAULT_TASK_ROOT = ".memtrace"
DEFAULT_CREATION_POLICY = "strict"  # strict | permissive
DEFAULT_GIT_POLICY = "ignore"  # track | ignore | none

_VALID_CREATION = {"strict", "permissive"}
_VALID_GIT = {"track", "ignore", "none"}


def _parse_scalar(raw: str) -> object:
    value = raw.strip()
    if value.startswith('"') and value.endswith('"') and len(value) >= 2:
        return value[1:-1]
    if value.startswith("'") and value.endswith("'") and len(value) >= 2:
        return value[1:-1]
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    try:
        return int(value)
    except ValueError:
        return value


def _parse_toml_subset(text: str) -> dict:
    """解析顶层键值 TOML 子集。表头（[section]）忽略——v1 无表段配置。"""
    data: dict = {}
    for raw_line in text.lstrip("\ufeff").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("["):
            continue  # v1 无表段；忽略而非报错，保持稀疏
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        # 去行内注释（引号外）
        value = raw_value
        quote = None
        for i, ch in enumerate(raw_value):
            if quote:
                if ch == quote:
                    quote = None
                continue
            if ch in ("'", '"'):
                quote = ch
                continue
            if ch == "#" and (i == 0 or raw_value[i - 1].isspace()):
                value = raw_value[:i]
                break
        if key:
            data[key] = _parse_scalar(value)
    return data


def config_path(project_root: Path) -> Path:
    return project_root / CONFIG_DIR / CONFIG_NAME


def load_config(project_root: Path) -> dict:
    """读取配置；文件不存在时返回全默认值（不报错，命令自行判断未 init）。"""
    defaults = {
        "task_root": DEFAULT_TASK_ROOT,
        "creation_policy": DEFAULT_CREATION_POLICY,
        "git_policy": DEFAULT_GIT_POLICY,
    }
    path = config_path(project_root)
    if not path.is_file():
        return defaults
    data = _parse_toml_subset(path.read_text(encoding="utf-8"))
    for key in defaults:
        if key in data:
            defaults[key] = data[key]
    return defaults


def write_config(project_root: Path) -> Path:
    """init 用：写入稀疏默认配置（仅 task_root，其余省略走默认）。"""
    path = config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# memtrace 项目配置（稀疏 TOML；未写的键走默认值）\n"
        f'task_root = "{DEFAULT_TASK_ROOT}"\n'
        "# creation_policy = \"strict\"   # strict | permissive\n"
        "# git_policy = \"ignore\"        # track | ignore | none\n"
    )
    _atomic_write(path, body)
    return path


def task_root_dir(project_root: Path, config: dict | None = None) -> Path:
    cfg = config if config is not None else load_config(project_root)
    root = str(cfg.get("task_root", DEFAULT_TASK_ROOT))
    if os.path.isabs(root):
        return Path(root)
    return project_root / root


def validate_config(config: dict) -> list[str]:
    errors = []
    if config.get("creation_policy") not in _VALID_CREATION:
        errors.append(f"creation_policy 必须是 {'/'.join(sorted(_VALID_CREATION))}")
    if config.get("git_policy") not in _VALID_GIT:
        errors.append(f"git_policy 必须是 {'/'.join(sorted(_VALID_GIT))}")
    return errors


def _atomic_write(path: Path, content: str) -> None:
    """单文件原子替换：先写临时文件再 os.replace（Windows/Linux 均可）。"""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8", newline="\n")
    os.replace(tmp, path)
