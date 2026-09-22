"""memtrace：结构化任务过程记录器（含任务管理）。

替代旧任务+记录层。数据模型沿用 tk schema v1（split 模式）：
- 项目配置 .agents/memtrace_config.toml（稀疏 TOML，task_root 默认 .memtrace）
- 任务目录 <task_root>/YYYY/MM/DD-NN--slug/
- 元数据 memtrace.toml + 正文 TASK.md
- WAL wal/YYYY-MM-DD.md 追加式 Markdown

规格来源：grill-memtrace.md「memtrace 规格 v1.0」（2026-09-22 定稿）。
"""

__version__ = "1.0.0"
