# agent-Joshu：个人 AI 工作流主包

## 前言

你在使用 Agent 时，是否遇到过这些情况？

- 大模型给出的结果和你的目标总是存在差距，反复补充要求后仍达不到预期。
- 任务一旦缺少持续交互，随着上下文变长，Agent 会逐渐偏离目标，而你很晚才发现。
- 为了纠正大模型幻觉，只能重新复制一大段材料并开启新会话，但新会话会丢失旧会话里的隐含信息、取舍过程和失败经验。
- Token 花得越来越多，任务却没有更稳定地朝预想方向推进。

这些问题不全是模型能力问题。很多时候，真正缺少的是一套稳定的使用方法：哪些上下文需要长期保存，事实和推断如何区分，什么时候必须停下来验证，任务跑偏后怎样恢复，以及一次任务里的经验如何进入下一次任务。

我在入职后真实的线上开发中逐渐意识到，人与人之间的经验差距只能靠时间积累，但具体的动手能力越来越体现在如何使用 Agent。回头看，我原来的方法其实很原始，主要是和 Agent 直接对话，再加上一些简单的工具调用。上下文、验证、授权、任务记录和经验复用都没有形成固定方法，模型的能力也没有被稳定地发挥出来。

因此，我以 [ruokee-agent-kit](https://github.com/ruokee/ruokee-agent-kit) 的结构和能力模式为起点，结合自己在模型部署、推理优化、框架与算子优化方向的使用经验，补充了 `inference-ops`、项目模板、ADR、证据规范和回归检查等，形成了这套更适合个人长期使用的 Agent 工作包。

它主要解决以下问题：

- 把长期规则、项目决策和临时任务过程分开保存，减少上下文污染，也降低切换会话时的信息损失。
- 按任务类型加载对应 Skill，不让所有规则一次性塞进上下文。
- 要求重要结论附带代码、配置、命令输出、版本或来源，避免把猜测写成事实。
- 用固定模板把同一套工作方式带到不同设备和项目，不依赖某台机器上的绝对路径。
- 在条件允许时，把方案设计、独立验证和实际执行拆开，尽早发现 Agent 已经跑偏。

这套工具并不追求让 Agent 完全无人看管，也不打算用一堆规则替代工程判断。它更像一个个人工作台，让 Agent 在长任务、跨会话和多项目环境里保持方向，并让每一次失败、修正和决定都有地方可查。

现在我把它分享出来，希望能帮到和我曾经一样，只会不断补提示词、重开会话，却仍然无法稳定获得理想结果的人。

### 适用人群

- 经常使用 Codex、Claude Code、OMP 等编码 Agent，并开始处理长任务或跨会话任务的开发者。
- 从事大模型部署、推理优化、框架或算子优化，希望把排障和性能分析过程固定下来的人。
- 想建立个人 Agent 工作流，又不希望一开始就搭建复杂平台的个人开发者和小团队。
- 在意事实依据、版本差异、操作授权和结果可复现性的人。

### 适用范围

- 需求梳理、技术调研、架构设计、Python 工程实践、代码质量评审和文档改写。
- 大模型推理服务的部署排障、性能分析、基线测量、问题报告和知识沉淀。
- 项目上下文管理、架构决定记录、跨设备安装和新项目初始化。
- 单 Agent 工作流，以及 Herdr 可用时的多 Agent 设计、验证和执行分工。

涉及依赖安装、环境修改、容器重建、服务重启或生产变更时，本项目只提供分级和检查方法，实际操作仍需要明确授权。

把这套工作包装进任意项目只需一条命令，安装与更新步骤见 [template/README.md](./template/README.md)。

## 目录

```text
├── README.md            本文件
├── LICENSE              本项目 MIT License
├── THIRD_PARTY_NOTICES.md 第三方来源与许可声明
├── AGENTS.md            主包工作区规则（架构、Skill 路由、证据纪律、授权分级、存储约定）
├── .agents/adr/         架构决定记录（proposal/decision/archived/rejected 生命周期 + 术语表）
├── .agents/rule/        工作规则（代码管理、测试、Python 风格、项目结构、工程取舍、文档撰写）
├── src/memtrace/        memtrace Python 包（任务过程记录 CLI + bootstrap 部署子命令，零第三方依赖）
├── Makefile             开发检查链入口（make check / make check-docs）
├── pyproject.toml       开发依赖组与 ruff 配置（uv 管理；memtrace 运行时零依赖不变）
├── uv.lock              开发依赖锁定
├── template/            项目上下文模板（agent-joshu/ 目录源 + agents-rules.md + 安装说明 + 版本标记）
├── reports/             主包自托管工作的问题报告（YYYY-MM-DD-NN-theme.md，事实-only）
├── tests/               memtrace 行为测试与 bootstrap 回归（pytest）；Skill 触发矩阵与场景回归卡（omp-loading.md、scenarios.md）
├── .memtrace/           任务过程（memtrace 数据，本地，不进 git）
├── .memtrace-archive/   旧任务只读归档（本地，不进 git）
└── .omp/                skills/（9 个 Skill，OMP 项目级自动发现）+ extensions/memtrace/
```

## Skill 库

用户显式触发：

- inference-ops：推理运维，部署排障与性能优化，含模式化工作流、方法论文档与知识库协议。
- grill-me：需求盘问，把不完整的想法和计划盘成可执行规格。
- summarizer：会话蒸馏问答，扫描本项目 omp、claude、codex 会话，知识性问答按时间追加进项目根 QA.md。

其余按对话信号自动加载：

- architect：架构分析、设计、评审与技术选型。
- python-engineering：Python 工程实践，覆盖结构、依赖、类型、测试与工具链。
- code-quality：代码质量，覆盖原则、模式、重构与测试设计。
- deep-research：深度调研，来源采集、交叉验证与论断边界。
- unslop：改写面向用户的文本，去除 AI 痕迹、换回人话；上游要求始终应用。
- memtrace：任务过程记录，create、log、read、search、update 子命令与阶段性 WAL（变更、推翻、验证、用户纠正）。

## 多代理闭环（herdr 可用时）

```text
用户需求
  → claude（study:p2）：按 Skill 设计方案/报告
  → codex（study:p3）：独立验证（只读，PASS/FAIL + 证据 + 必须修正项）
  → omp（study:p1）：修正落地执行（L2/L3 命令另行授权）
  → 产出归档（reports/ 调研目录）
```

- 前置探测：`test "$HERDR_ENV" = 1`；herdr 不可用时单代理照常。
- 设计稿与验证报告分别落盘，各自独立成文件；验证只读不改。

## 维护

- 知识条目（`inference-ops` 的 `references/knowledge/`）按需生成（一场景一条目），引擎大版本发布后标 `needs-review` 复核。
- 报告解决后从 `reports/` 删除或移入对应任务材料。
- 新的长期边界决定按 [.agents/adr/README.md](./.agents/adr/README.md) 的生命周期入 ADR 目录；场景回归用 [tests/scenarios.md](./tests/scenarios.md)。
- `template/` 内容变更时同步更新 `template/agent-joshu/VERSION`；已安装项目重跑 `bootstrap` 比对更新（见 [template/README.md](./template/README.md)「更新」节）。

## 来源与致谢

感谢 [ruokee-agent-kit](https://github.com/ruokee/ruokee-agent-kit)（MIT License），本项目的通用 Skill 与工作流思路以其为起点。第三方版权与许可文本见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 许可证

本项目采用 [MIT License](./LICENSE)。
