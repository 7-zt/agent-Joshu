# agent-Joshu 主包工作区规则

本仓库是个人 AI 工作流主包（推理优化 + 部署排障方向）：全局能力层 + 项目上下文模板。Agent 在本目录及其子目录工作时遵循以下规则。

## 架构：主包与项目侧

- 部署单元＝项目（决定见 `.agents/adr/decision/2026-09-22-project-self-contained-bootstrap.md`）：主包＝复杂源仓（维护成本留在主包）；项目＝自含轻量包。
- 主包（本仓库）：Skill 能力层（`.omp/skills/`，OMP 项目级自动发现，与项目侧同构）+ 跨项目决策与经验（`.agents/adr/`）+ 项目上下文模板（`template/`）+ 代码组件（`memtrace/` Python 包、`memtrace bootstrap` 子命令与 `.omp/extensions/memtrace/`）。git clone 即用，零设备级配置。
- 项目侧（自含）：`PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>` 一条命令装入完整工具包——可见的 `agent-joshu/`（模板 + adr + vendored `memtrace/` CLI + VERSION + manifest）+ `.omp/skills/`（8 Skill，OMP 项目级自动发现）+ `.omp/extensions/memtrace/`（优先调用项目内 CLI）。安装与更新步骤见 `template/README.md`；重跑＝比对更新，项目自有内容永不覆盖。项目 clone 到任意设备（含内网机）即得全部能力，只需 OMP + Python 3.10+。
- 记录策略：决策进 ADR（主包 `.agents/adr/`、项目 `agent-joshu/adr/`，同构）；任务过程只留本地，不进 git。
- 回流：项目经验可泛化到多个项目时，回流主包 ADR 或对应文档，不在单个项目私藏。

## 语言约定

Skill frontmatter 标识与文件名用英文；正文用中文；首次出现的领域术语给中英对照。
例外：自 ruokee-agent-kit 移植的 Skill（grill-me、python-engineering、architect、code-quality、deep-research）保留英文正文，便于与上游同步（见 .agents/adr/decision/2026-09-21-port-five-skills-english-body.md）。
同日自本地 codex 移植的 unslop 同规则保留英文正文。

## Skill 路由（自动触发）

除 inference-ops 与 grill-me（用户触发）外，本仓库其余 Skill 均允许模型隐式调用。对话或任务流中出现匹配信号时，先读 `skill://<name>` 再作答，不等用户显式 `/skill:` 调用：

| Skill | 触发信号 |
| --- | --- |
| grill-me | 想法/需求/计划不完整，需要盘问澄清成可执行规格（仅用户显式 `/skill:grill-me` 触发） |
| architect | 架构设计、系统分析、技术选型、架构评审与演进 |
| python-engineering | Python 工程实践：结构、依赖、类型、测试、工具链 |
| code-quality | 代码质量评估、重构、设计原则与模式、测试设计 |
| deep-research | 深度调研、需要来源交叉验证的调研报告 |
| unslop | 撰写或改写任何面向用户的文本（报告、文档、消息）：去除 AI 痕迹、换回人话；上游声明「必须始终应用」 |
| inference-ops | 推理系统排障/性能优化（仅用户显式触发） |
| memtrace | 任务过程记录：建任务、阶段性 log（变更/推翻/验证/用户纠正）、接手任务读上下文、检索历史 |

任务阶段映射（memtrace 任务流内作为领域增强按需叠加）：

- 需求梳理：grill-me（需用户显式 `/skill:grill-me`，模型不自动加载）
- 技术调研：deep-research
- 方案/架构设计：architect
- 实现阶段（Python 项目）：python-engineering
- 检查/评审：code-quality

## 组件自包含（硬规则）

- 每个 Skill 必须有 `SKILL.md`，并且单独复制后仍可使用。
- `workflow/`、`references/` 与 `glossary.md` 按内容需要创建，不为满足目录形式添加空文件。Skill 引用这些内容时，目标必须位于当前 Skill 目录内并真实存在。
- `agents/openai.yaml` 在 Skill 需要 OpenAI 展示信息或触发策略时创建；用户显式触发型 Skill 必须提供该文件。文件存在时必须通过 YAML 解析。
- Skill 内部文件引用、书面路径引用、执行前置规则不得依赖组件目录外文件（`../` 跨 Skill 引用、兄弟 Skill 名引用、「调用 XX Skill」「见 YY/references/ZZ」类指令都禁止）。
- 必要的最小规则复制进组件内，不复制整份文档。例：reporting 参考自带环境字段采集示例，不依赖其他参考文档。
- 组合用法（设计→验证→执行循环，Skill 间协作）只在工作区级 README 或 omp/prompts 说明，不写入组件正文。
- herdr 启动子代理时，工作目录必须是本仓库根（以当前设备上的克隆位置为准，勿写死绝对路径），确保加载本 AGENTS.md。

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

- 长期决定：`.agents/adr/`（生命周期见其 README；单用户由用户当次明确确认）。
- 问题报告：`reports/YYYY-MM-DD-NN-theme.md`（事实-only，见 inference-ops 的 reporting 参考）。主包自身维护的问题放这里；项目内的问题归项目 `agent-joshu/reports/`。
- 调研报告与来源快照：调研任务自建目录，快照存 `sources/` 子目录。
- 可复用 prompt：`omp/prompts/`（写入需用户确认）。
- 任务过程（memtrace 任务、WAL、任务材料目录，位于 `.memtrace/`）属过程状态，留在本地，不进 git。旧任务只读归档于 `.memtrace-archive/`，同样不进 git。

## memtrace 集成（任务过程记录）

- 本仓库自带 `memtrace/` Python 包（Python 3.10+，零第三方依赖）与 `.omp/extensions/memtrace/` OMP 扩展；安装契约不变（clone 即得）。决定见 `.agents/adr/decision/2026-09-22-master-kit-ships-code.md`。
- 跨阶段/跨会话任务用 `memtrace create` 建任务，阶段性 `memtrace log` 写变更/推翻/验证/用户纠正小节；单会话琐碎任务不建。
- 接手任务先 `memtrace read <任务> --wal`；查历史用 `memtrace search`。会话开始的当前任务注入由 OMP 扩展完成。
- 数据模型与命令语义见 `skills/memtrace/SKILL.md`；不手工伪造 `.memtrace/` 结构，不改动 schema 字段。

## 多代理协作（herdr 可用时）

- 前置：`test "$HERDR_ENV" = 1`；失败则单代理工作流照常。
- 流程：设计（claude）→ 独立验证（codex，只读，PASS/FAIL+证据）→ 执行（omp，落地）。
- 验证者不重做设计；发现缺陷给具体修正建议。执行前修正必须完成。
- 任何一步命令与预期不符：停止并报告，不猜替代命令。

## 报告与文档

- 报告写读者视角：三个月后的自己无会话上下文也能懂。
- 报告中不混入会话过程性信息（COT 泄露清理）。
- 执行计划不含「待决定事项」——计划应可直接交给任意 Agent 开工。

## 长任务模式（跨会话任务）

- **触发**：任务预计需要跨多个会话（性能调优、复杂排障、大型调研）。
- **工具**：memtrace（见「memtrace 集成」节）。项目未 init 时先 `memtrace init`。
- **结构**（memtrace 任务目录）：
  - `TASK.md`：当前目标、稳定决策、材料入口、有效阻塞
  - `wal/YYYY-MM-DD.md`：追加式记录变更、推翻、验证结果、用户纠正、里程碑、阻塞（阶段性汇总，不记命令流水）
  - 材料子目录（`sources/`、`research/` 等）：按需创建
- **短任务不创建**：单会话内完成的任务不建任务目录。
- **不进 git**：`.memtrace/` 任务目录与 WAL 属过程状态，留本地。
