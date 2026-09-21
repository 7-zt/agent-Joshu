<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

# workflow 工作区规则

本目录是用户的个人 AI 工作流工作区（推理优化 + 部署排障方向）。Agent 在本目录及其子目录工作时遵循以下规则。

## 语言约定

Skill frontmatter 标识与文件名用英文；正文用中文；首次出现的领域术语给中英对照。
例外：自 ruokee-agent-kit 移植的 Skill（grill-me、python-engineering、architect、code-quality、deep-research）保留英文正文，便于与上游同步（见 DECISIONS.md 2026-09-21）。
同日自本地 codex 移植的 unslop 同规则保留英文正文。

## Skill 路由（自动触发）

除 inference-ops 与 grill-me（用户触发）外，本仓库其余 Skill 均允许模型隐式调用。对话或 Trellis 任务流中出现匹配信号时，先读 `skill://<name>` 再作答，不等用户显式 `/skill:` 调用：

| Skill | 触发信号 |
| --- | --- |
| grill-me | 想法/需求/计划不完整，需要盘问澄清成可执行规格（仅用户显式 `/skill:grill-me` 触发） |
| architect | 架构设计、系统分析、技术选型、架构评审与演进 |
| python-engineering | Python 工程实践：结构、依赖、类型、测试、工具链 |
| code-quality | 代码质量评估、重构、设计原则与模式、测试设计 |
| deep-research | 深度调研、需要来源交叉验证的调研报告 |
| unslop | 撰写或改写任何面向用户的文本（报告、文档、消息）：去除 AI 痕迹、换回人话；上游声明「必须始终应用」 |
| inference-ops | 推理系统排障/性能优化（仅用户显式触发） |

Trellis 任务流映射（作为领域增强按需叠加，流程仍以 trellis-* Skill 为准）：

- 需求梳理（brainstorm 阶段）：grill-me（需用户显式 `/skill:grill-me`，模型不自动加载）
- 技术调研（research）：deep-research
- 方案/架构设计：architect
- 实现阶段（Python 项目）：python-engineering
- 检查/评审（check 阶段）：code-quality

## 组件自包含（硬规则）

- 每个 Skill 目录必须自包含：SKILL.md、workflow、references、glossary、agents/openai.yaml（用户触发型必需）。
- Skill 内部文件引用、书面路径引用、执行前置规则不得依赖组件目录外文件（`../` 跨 Skill 引用、兄弟 Skill 名引用、「调用 XX Skill」「见 YY/references/ZZ」类指令都禁止）。
- 必要的最小规则复制进组件内，不复制整份文档。例：reporting 参考自带环境字段采集示例，不依赖其他参考文档。
- 组合用法（设计→验证→执行循环，Skill 间协作）只在工作区级 README 或 omp/prompts 说明，不写入组件正文。
- herdr 启动子代理时，工作目录必须是 `C:/Users/admin/Desktop/yuting/program/agent-Joshu`（本仓库根），确保加载本 AGENTS.md。

## 证据纪律（所有任务的底线）

- 区分：观测事实（带命令输出/`path:line`/日志引用）、推导、未验证假设、建议、用户决策。
- 版本相关断言必须附版本；版本不明写「需确认当前版本」，不给确定行为断言。
- 性能数字必须满足 inference-ops 的 benchmark-protocol 证据集，否则只能以「未完成测量」呈现。
- 不确定就说不确定；宁可输出「未定位 + 下一步计划」，不包装成确定结论。

## 授权边界

- 「分析/排查/调研」请求不自动授权环境变更。命令按 L0-L3 分级（见 inference-ops Skill）；L2/L3 需当次明确确认。
- 报告写入授权与环境修改授权是两件事。
- 删除文件、覆盖内容、跨任务移动材料，先问。

## 存储约定

- 问题报告：`reports/YYYY-MM-DD-NN-theme.md`（事实-only，见 inference-ops 的 reporting 参考）。
- 调研报告与来源快照：调研任务自建目录，快照存 `sources/` 子目录。
- 可复用 prompt：`omp/prompts/`（写入需用户确认）。
- 构建过程材料 `_pipeline/` 归档于仓库外 `C:/Users/admin/Desktop/workspace/workflow/_pipeline/`（只读，不修改、不迁移）。

## 多代理协作（herdr 可用时）

- 前置：`test "$HERDR_ENV" = 1`；失败则单代理工作流照常。
- 流程：设计（claude）→ 独立验证（codex，只读，PASS/FAIL+证据）→ 执行（omp，落地）。
- 验证者不重做设计；发现缺陷给具体修正建议。执行前修正必须完成。
- 任何一步命令与预期不符：停止并报告，不猜替代命令。

## tk 集成（可选）

- 探测 `command -v tk` 成功才使用；通过 tk 工具管理任务，不手工创建 `.tk` 结构。
- 未安装时用本目录的 reports/ 与任务材料目录；不伪造 tk 数据。

## 报告与文档

- 报告写读者视角：三个月后的自己无会话上下文也能懂。
- 报告中不混入会话过程性信息（COT 泄露清理）。
- 执行计划不含「待决定事项」——计划应可直接交给任意 Agent 开工。

## 长任务模式（跨会话任务）

- **触发**：任务预计需要跨多个会话（性能调优、复杂排障、大型调研）。
- **创建**：首次出现时在工作区根或 reports/ 旁建任务目录（不用 `.tk` 格式，普通目录即可）。
- **结构**：
  - `README.md` 或 `TASK.md`：当前目标、稳定决策、材料入口、有效阻塞
  - `log.md`：追加式记录用户决定、修正、验证结果、里程碑、阻塞（不记命令流水）
  - `sources/`：来源快照
  - `results/`：产出与验证
- **短任务不创建**：单会话内完成的任务不建目录。
- **tk 可用时优先**：如果检测到 `tk` 命令可用，优先用 tk 工具管理任务；否则用上述普通目录。
