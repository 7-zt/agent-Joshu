"""时间工具：RFC3339 本地时间戳（带本地时区偏移）。"""

from __future__ import annotations

import time


def rfc3339_now() -> str:
    """本地时区 RFC3339 时间戳，如 2026-09-22T14:30:05+08:00。

    用 time 而非 datetime：避开 Windows 本地时区数据库差异，
    结构化输出直接取 time.strftime 的 %z。
    """
    now = time.localtime()
    offset = time.strftime("%z", now)
    if offset and len(offset) == 5:
        offset_formatted = f"{offset[:3]}:{offset[3:]}"
    else:
        offset_formatted = "Z"
    base = time.strftime("%Y-%m-%dT%H:%M:%S", now)
    return f"{base}{offset_formatted}"


def today_local() -> str:
    return time.strftime("%Y-%m-%d", time.localtime())


def today_parts() -> tuple[str, str, str]:
    """本地日期 (YYYY, MM, DD)。"""
    t = time.localtime()
    return (time.strftime("%Y", t), time.strftime("%m", t), time.strftime("%d", t))
