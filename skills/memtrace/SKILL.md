---
name: memtrace
description: 结构化任务过程记录器（含任务管理）：何时创建任务、阶段性写 WAL（变更/推翻/验证/用户纠正）、会话开始读当前任务、跨任务检索。凡涉及「记一下进展」「接上次任务」「为什么当时这么改」的工作流信号先读本 Skill。
---

# memtrace：任务过程记录

memtrace 是本仓库自研的任务过程记录器：每项目根 `.memtrace/` 本地目录（不进 git），按任务聚拢过程痕迹，产出「压缩上下文」——AI 换会话可注入续接，人可按目录直接翻。

## 何时用

- 开始一个会跨阶段/跨会话的任务时：`create` 建任务。
- 每完成一个阶段（一组相关改动+验证）时：`log` 写阶段性汇总。
- 会话开始/接手半截任务时：`read` 拉当前任务与 WAL。
- 用户问「之前为什么这么改」「上次推翻过什么方案」时：`search` 检索。
- 单会话内完成的琐碎问答不建任务。

## 命令速查

在项目根执行（Python 3.10+，无第三方依赖；包位于主包仓库 `memtrace/`，`PYTHONPATH` 指向主包根或已 pip 安装）：

```bash
memtrace init                          # 首次：写 .agents/memtrace_config.toml
memtrace create "任务名" --status open # 建任务目录 .memtrace/YYYY/MM/DD-NN--slug/
memtrace log <任务引用> "一句话消息" --actor <谁> \
  [--changes "…"] [--reversals "…"] [--verification "…"] [--user-correction "…"] [--body "…"]
memtrace read --list                   # 全部任务
memtrace read <任务引用> --wal --full  # 任务详情 + WAL 全文
memtrace search "关键词" [--regex] [-C 2]
memtrace update <任务引用> --status closed --reason "原因" --actor <谁>
```

任务引用：目录名、`YYYY/MM/DD-NN--slug` 相对路径、或 id 前缀（够长不歧义即可）。

## 数据模型（读写都别破坏它）

- `.agents/memtrace_config.toml`：稀疏配置；`task_root` 默认 `.memtrace`。
- 任务目录：`.memtrace/YYYY/MM/DD-NN--slug/`；子任务 `NN--slug/`；材料子目录（`sources/`、`research/` 等）自由创建。
- 元数据 `memtrace.toml`：七字段 schema v1（schema_version/id=UUIDv7/name/status/created_at/depends_on/related_to，可选 extra）。status 只有 planning/open/closed；closed 是终态，关闭必须给原因。
- 正文 `TASK.md`：目标、稳定决策、材料入口。人直接可读。
- WAL `wal/YYYY-MM-DD.md`：追加式 Markdown，条目 `## <RFC3339 时间戳> · <actor>` + 消息 + 可选正文。**只追加，不改历史。**

## WAL 语义小节（阶段性 log 的硬格式）

阶段汇总的正文按小节组织，只写有内容的小节（`log` 命令的 `--changes` 等参数自动拼）：

- **变更**：改了哪些文件 + 为什么改。
- **推翻**：旧方案 → 新方案 + 为什么放弃旧的。
- **验证**：跑了什么（命令/测试）+ 结果（含失败）。
- **用户纠正**：用户中途纠正了什么。

粒度纪律：阶段汇总而非每轮流水；每条要能在三个月后回答「当时做了什么、为什么」。

## actor 约定

- `mt-impl`：实现会话的阶段记录。
- `memtrace-hook`：OMP 扩展自动抓的客观元数据（文件清单、命令摘要）。
- `user`：用户口述的决定。
- 其他具名 agent（如 `codex-verify`）：验证者记录。

## 与其他记录的分工

- 长期决策 → ADR（进 git），不写进 WAL。
- 事实-only 问题报告 → `reports/`。
- 评审过程材料 → 放任务目录的材料子目录。
- memtrace 只记过程；不要把 ADR/reports 的内容复制进 WAL。

## 失败处理

- 「未找到 memtrace 项目」：项目根执行 `memtrace init`。
- strict 模式拒绝 create：先关闭活跃任务（给原因），或确认后 `--permissive`。
- 命令与预期不符：停止并报告，不猜数据结构、不手改 `memtrace.toml` schema 字段。
