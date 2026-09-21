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

现在我把它分享出来，希望能帮到曾经和我一样，只会不断补提示词、重开会话，却仍然无法稳定获得理想结果的人。

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

推理优化 × 部署排障方向的个人 Agent Kit。**一份克隆装好能力，一套模板进入项目。** 核心理念：证据优先、事实与推断分离、版本敏感断言必须可审计、跨设备零路径耦合。

## 架构

- **主包（本仓库）**：装在每台设备上的全局能力层——Skill 库（OMP 加载）+ 跨项目决策与经验（ADR）+ 项目上下文模板（`template/`）。只沉淀跨项目通用的工作流、决策与经验。
- **项目侧**：每个项目根目录一个可见的 `agent-joshu/`（与 src、docs 同级）＝ 复制模板 + `trellis init`。项目规则与决策随项目 git 走；任务过程留本地（决策进 `agent-joshu/adr/`）。

```text
每台设备                                 每个项目
├── agent-Joshu 主包（git clone）         ├── src/  docs/  README …
│   ├── skills/ ──OMP 全局加载──┐         └── agent-joshu/（复制模板而来）
│   ├── .agents/adr/            │                ├── adr/（决策，进项目 git）
│   └── template/ ──────────────┘                └── VERSION（模板版本标记）
└── omp/setup.md：新设备 3 步引导            .trellis/ 任务过程（本地）
```

## 目录

```
├── README.md            本文件
├── LICENSE              本项目 MIT License
├── THIRD_PARTY_NOTICES.md 第三方来源与许可声明
├── AGENTS.md            主包工作区规则（架构、Skill 路由、证据纪律、授权分级、存储约定）
├── .agents/adr/         架构决定记录（proposal/decision/archived/rejected 生命周期 + 术语表）
├── skills/              Skill 库（OMP 全局加载，见 omp/setup.md；6 个移植 vendored + inference-ops 原创）
├── template/            项目上下文模板（agent-joshu/ 目录源 + agents-rules.md + 安装说明 + 版本标记）
├── reports/             主包自托管工作的问题报告（YYYY-MM-DD-NN-theme.md，事实-only）
├── omp/                 setup.md（新设备 3 步引导）、prompts/（可复用模式索引 + 独立 prompt）
├── tests/               逐 Skill 触发矩阵（omp-loading.md）与场景回归卡（scenarios.md）
├── tools/               check-workflow.ps1 结构/链接/模板/ADR/绝对路径自检
├── .trellis/            Trellis 流程（任务与日志本地化，不进 git）
└── .omp/                Trellis 的 OMP 组件（trellis 生成，勿手改）
```

## 快速开始

**新设备（3 步）**：见 [omp/setup.md](./omp/setup.md) —— 克隆 → 配置 OMP（命令自动取当前路径）→ 跑触发矩阵。

**新项目（3 步）**：见 [template/README.md](./template/README.md) —— 复制 `agent-joshu/` → `trellis init` 并并入规则 → 触发矩阵 + git 状态检查。

## Skill 库

| Skill | 触发 | 说明 |
| --- | --- | --- |
| inference-ops | 用户显式 | 推理运维：部署排障 × 性能优化（3 模式 + 10 篇方法论文档 + 知识库协议） |
| grill-me | 用户显式 | 需求盘问：把不完整想法/计划盘成可执行规格 |
| architect | 自动 | 架构：系统分析、设计、评审、技术选型 |
| python-engineering | 自动 | Python 工程实践：结构/依赖/类型/测试/工具链 |
| code-quality | 自动 | 代码质量：原则、模式、重构、测试设计 |
| deep-research | 自动 | 深度调研：来源采集、交叉验证、论断边界 |
| unslop | 自动 | 去除文本 AI 痕迹、换回人话（上游声明「必须始终应用」） |

后六个自 ruokee-agent-kit（五个）与本地 codex（unslop）移植，英文正文保留以便与上游 diff 同步（见对应 ADR）。

## 防幻觉机制一览

| 机制 | 落点 |
| --- | --- |
| 数字断言最低证据集（环境+命令+负载+统计+样本数） | inference-ops `references/benchmark-protocol.md` |
| 请求级分布 vs 跨运行统计分开；改进小于波动不称提升 | 同上 §3 |
| A/B 单变量原则，混杂因素必列 | 同上 §5 |
| 命令五元组（文本/退出码/stdout/stderr/位置）与脱敏 | inference-ops `references/evidence-and-snapshot.md` |
| 命令分级 L0-L3；「排查」≠授权改环境 | inference-ops SKILL.md、AGENTS.md |
| 根因需反向验证；未验证只能是「最可能原因」 | inference-ops `workflow/full.md` |
| 事实-only 报告，禁止定位/方案混入 | inference-ops `references/reporting.md`、reports/ |
| 论断五分类（事实/推断/判断/宣传/未解决） | inference-ops `references/reporting.md` |
| 来源快照审计链（原文/摘要+URL+作者+日期） | inference-ops `references/reporting.md` |
| 知识条目审计元数据（source/version/status） | inference-ops `references/knowledge-base.md` |
| 版本不明 → 「需确认当前版本」，不给行为断言 | inference-ops SKILL.md + AGENTS.md |
| 零发现合法；不编造凑数 | inference-ops 停止规则 |

## 多代理闭环（herdr 可用时）

```
用户需求
  → claude（study:p2）：按 Skill 设计方案/报告
  → codex（study:p3）：独立验证（只读，PASS/FAIL + 证据 + 必须修正项）
  → omp（study:p1）：修正落地执行（L2/L3 命令另行授权）
  → 产出归档（reports/ 调研目录）；可复用模式沉淀 omp/prompts/
```

- 前置探测：`test "$HERDR_ENV" = 1`；herdr 不可用时单代理照常。
- 设计稿与验证报告分别落盘（各自独立成文件），验证只读不改。
- 本工作区即由该闭环构建：01 总结(omp) → 03 设计(claude) → 04 验证(codex) → 落地(omp)。

## 维护

- 知识条目（`inference-ops` 的 `references/knowledge/`）按需生成（一场景一条目），引擎大版本发布后标 `needs-review` 复核。
- 报告解决后从 `reports/` 删除或移入对应任务材料。
- OMP 升级后重验 `skills.customDirectories`（`omp config get ... --json`），不猜键名。
- 修改任何 SKILL 或文档后运行 `tools/check-workflow.ps1`（覆盖 frontmatter、链接、自包含边界、知识条目元数据、ADR 与模板结构、绝对路径扫描），退出码 0 才算通过。
- 新的长期边界决定按 `.agents/adr/README.md` 的生命周期入 ADR 目录；场景回归用 `tests/scenarios.md`。
- `template/` 内容变更时同步更新 `template/agent-joshu/VERSION`；已安装项目按 `template/README.md` 手动比对更新。

## 来源与致谢

主要的通用 Skill 与部分工作流思路来自 [ruokee-agent-kit](https://github.com/ruokee/ruokee-agent-kit)，上游采用 MIT License。本仓库在此基础上加入 `inference-ops`、`unslop`、主包与项目侧双层结构、ADR、模板、证据规范和验收脚本。第三方版权与许可文本见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 许可证

本项目采用 [MIT License](./LICENSE)。
