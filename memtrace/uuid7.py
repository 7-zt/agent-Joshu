"""UUIDv7 生成（Python 3.10+ 标准库无内置 uuid7，按 RFC 9562 手写）。

48 位 Unix 毫秒时间戳 + 12 位随机 a_ver + 2 位变体 + 62 位随机。
"""

from __future__ import annotations

import os
import time
import uuid


def uuid7() -> str:
    ms = time.time_ns() // 1_000_000
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    value = (ms & 0xFFFFFFFFFFFF) << 80
    value |= 0x7 << 76  # version 7
    value |= rand_a << 64
    value |= 0x2 << 62  # RFC 4122 variant
    value |= rand_b
    return str(uuid.UUID(int=value))
