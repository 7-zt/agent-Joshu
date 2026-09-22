# ADR 决定：memtrace 取代 Trellis 任务+记录层

反向决定：2026-09-21-master-kit-and-project-contexts.md（其中「流程引擎保留 Trellis」）

## 背景

2026-09-22 grill-me 评审（grill-memtrace.md，已移入本次实现任务的材料目录）结论：Trellis 对 AI 交互与工作过程的记录不完整——prd.md/journal 粒度太粗，无法支撑「换会话注入压缩上下文、定位哪一步出问题」的消费场景；`trellis mem` 对 OMP 会话不可用。用户要求自研结构化任务过程记录器 memtrace（数据模型参照 ruokee projects/tk 的 schema v1），完全卸载 Trellis，由 memtrace 的 OMP 扩展接管轻量注入。

## 决定

- **memtrace 定位**：结构化任务过程记录器（含任务管理）。产出压缩上下文：AI 可注入定位问题步骤，人可按任务目录直接阅读。
- **数据模型**（tk schema v1，split 模式）：项目配置 `.agents/memtrace_config.toml`（稀疏 TOML）；任务目录 `.memtrace/YYYY/MM/DD-NN--slug/`；元数据 `memtrace.toml` 七字段；正文 `TASK.md`；WAL `wal/YYYY-MM-DD.md` 条目 `## <RFC3339> · actor`，追加式，正文按语义小节组织（变更/推翻/验证/用户纠正）。
- **命令集 v1**：init/create/log/read/search/update；关闭任务必须给原因；strict 创建策略默认开启。
- **写入机制（混合）**：AI 写结构化语义（阶段性 log）+ OMP 扩展抓客观元数据（会话开始 git 变更快照，actor=memtrace-hook）。
- **OMP 注入**：会话开始注入当前任务与最近 WAL 摘要；每 10 轮输入阶段性提醒记录；按 `.memtrace/` 标记定位项目根，非 memtrace 项目零打扰。
- **Trellis 完全卸载**：删除 `.trellis/` 与 `.omp/` 下全部 trellis 组件；`.trellis/tasks/` 先整体挪为 `.memtrace-archive/` 本地归档（不进 git、不迁移进 memtrace 数据模型）；新项目安装不再 `trellis init`，改为 `memtrace init`。
- **记录分工**：ADR 进 git 不变；reports/ 事实报告不变；grill 评审记录变成任务材料；journal 概念取消（WAL 即过程日志）。
- **非目标（v1）**：原始对话/工具轨迹全量采集、MCP 服务器、多 harness 安装器、embed 模式、schema 迁移、GC、rename 引用扫描、跨项目集中检索。

## 真实替代项

- 保留 Trellis 任务+记录层、仅换注入指向——被拒：记录粒度不满足主诉求（2026-09-21 曾以「迁移无收益」拒绝 tk，本决定反向该条：自研目标不同，收益在记录模型而非工具替换）。
- 采用 ruokee tk 原工具——被拒：引入 Rust 运行时依赖，且中文工作流外的定制空间受限；只取其 schema 与 WAL 格式。
- 自建极简（TASK.md+log.md 纯手工）——被拒：全靠纪律无工具支撑，检索与注入缺失。

## 后果

- ✓ 任务过程记录有了明确归属与统一格式，「决策进 git、过程留本地」策略完整落地
- ✓ 会话开始自动注入当前任务上下文，接续半截任务不再依赖回忆
- ✓ 摆脱 trellis update 覆盖风险与外部运行时依赖
- ✗ 漏记风险靠 Skill 纪律 + hook 元数据托底（混合机制的固有代价）
- ✗ OMP ExtensionAPI 升级可能破坏扩展（与 Trellis 同风险面），靠 tests/omp-loading.md 矩阵回归
- ✗ 旧 `.trellis/tasks/` 变为只读归档，无法用 memtrace 检索

## 重审条件

出现多人协作的任务流需求；WAL 检索性能成为实际瓶颈（考虑索引）；OMP hook 机制变更导致注入层不可维护；Python 3.10+ 在目标设备不可用时重审技术栈。
