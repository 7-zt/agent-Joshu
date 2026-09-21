# agent-Joshu：个人 AI 工作流主包

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

能力模式源自 `ruokee-agent-kit`（MIT）
