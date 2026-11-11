"""pytest 配置：把 src 布局的 memtrace 包加入导入路径。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
