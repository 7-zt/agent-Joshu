# agent-joshu 项目规则

本文件由 agent-Joshu 主包模板提供，安装时并入项目根 AGENTS.md。

## Skill 能力（项目内自含）

Skills 位于项目 `.omp/skills/`，由 OMP 项目级自动发现。对话中出现匹配信号时先读 `skill://<name>` 再作答，不等用户显式 `/skill:` 调用：

| Skill | 触发方式 | 触发信号 |
| --- | --- | --- |
| inference-ops | 仅用户显式 `/skill:inference-ops` | 推理系统排障 / 性能优化 |
| grill-me | 仅用户显式 `/skill:grill-me` | 把不完整想法/计划盘成可执行规格 |
| architect | 自动 | 架构设计、系统分析、技术选型、架构评审与演进 |
| python-engineering | 自动 | Python 工程实践：结构、依赖、类型、测试、工具链 |
| code-quality | 自动 | 代码质量评估、重构、设计原则与模式、测试设计 |
| deep-research | 自动 | 深度调研、需要来源交叉验证的调研报告 |
| unslop | 自动 | 撰写或改写任何面向用户的文本（去 AI 痕迹） |
| memtrace | 自动 | 任务过程记录：建任务、阶段性 log、接手任务读上下文、检索历史 |

## 证据纪律（所有任务的底线）

- 区分：观测事实（带命令输出/`path:line`/日志引用）、推导、未验证假设、建议、用户决策。
- 版本相关断言必须附版本；版本不明写「需确认当前版本」，不给确定行为断言。
- 性能数字必须满足 inference-ops 的 benchmark-protocol 证据集，否则只能以「未完成测量」呈现。
- 不确定就说不确定；宁可输出「未定位 + 下一步计划」，不包装成确定结论。

## 授权边界

- 「分析/排查/调研」请求不自动授权环境变更。命令按 L0-L3 分级（见 inference-ops Skill）：L0 只读可直接执行；L1 本地可逆说明意图后执行；L2 改变环境需用户确认；L3 影响运行系统需明确授权 + 回退方法。
- 删除文件、覆盖内容、跨任务移动材料，先问。

## 存储约定（本项目）

- 决策记录：`agent-joshu/adr/`（生命周期见 `agent-joshu/adr/README.md`）；项目有 git 仓库时随项目 git 走，无 git 项目就只在本地目录维护（回滚与归因能力随之缺失，属项目侧取舍）。
- 任务过程：memtrace 任务在 `.memtrace/`（有 git 仓库且 `git_policy=ignore` 时被 gitignore 留在本地；`git_policy=track` 时随项目 git；无 git 项目本就无此区分）。跨阶段/跨会话任务用 `memtrace create` 建任务、阶段性 `memtrace log` 写变更/推翻/验证/用户纠正小节；接手任务先 `memtrace read`，查历史用 `memtrace search`。CLI 位于 `agent-joshu/memtrace/`，项目内调用使用 `PYTHONPATH=agent-joshu python -m memtrace`；扩展位于 `.omp/extensions/memtrace/`。
- 问题报告：`agent-joshu/reports/YYYY-MM-DD-NN-theme.md`（事实-only：现状/预期/环境/复现/已尝试；禁止混入定位、根因、方案）。
- 回流：能泛化到多个项目的经验，回流 agent-Joshu 主包（ADR 或对应文档），不在本项目私藏。

## 报告与文档

- 报告写读者视角：三个月后的自己无会话上下文也能懂。
- 报告中不混入会话过程性信息（COT 泄露清理）。
- 执行计划不含「待决定事项」——计划应可直接交给任意 Agent 开工。

## 语言约定

正文用中文；标识符与文件名用英文。
