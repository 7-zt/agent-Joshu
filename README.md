# 个人 AI 工作流（推理优化 × 部署排障）

为「大模型推理优化 + 部署问题排查」方向定制的防幻觉 AI 工作区。核心理念：**证据优先、事实与推断分离、版本敏感断言必须可审计**。

## 目录

```
workflow/
├── README.md            本文件
├── AGENTS.md            工作区 Agent 规则（证据纪律、授权分级、存储约定）
├── .agents/adr/         架构决定记录（proposal/decision/archived/rejected 生命周期）
├── skills/              Skill 库（OMP 加载，见 omp/setup.md）
│   ├── inference-ops/       推理运维：部署排障 × 性能优化（用户触发，3 模式 + 10 篇方法论文档 + 知识库协议）
│   ├── grill-me/            需求盘问：把不完整想法/计划盘成可执行规格（用户触发）
│   ├── architect/           架构：系统分析、设计、评审、技术选型（自动触发）
│   ├── python-engineering/  Python 工程实践：结构/依赖/类型/测试/工具链（自动触发）
│   ├── code-quality/        代码质量：原则、模式、重构、测试设计（自动触发）
│   ├── deep-research/       深度调研：来源采集、交叉验证、论断边界（自动触发）
│   └── unslop/               去除文本 AI 痕迹、换回人话（自动触发）
├── reports/             问题报告存储（YYYY-MM-DD-NN-theme.md）
├── omp/                 OMP 落地：setup.md（安装+版本探测）、prompts/（可复用模式索引 + 独立 prompt）
├── tests/               回归场景卡（scenarios.md）与 OMP 加载自检步骤（omp-loading.md）
└── tools/               check-workflow.ps1 结构/链接/自包含自动检查
```

## 快速开始

1. 按 [omp/setup.md](./omp/setup.md) 挂载 Skill 目录（配置键 `skills.customDirectories`，已在 OMP 18.2.3 验证）。
2. 重启 OMP，用 `/skill:inference-ops` 触发。
3. 在本目录工作时 [AGENTS.md](./AGENTS.md) 的规则自动生效；其中「Skill 路由（自动触发）」节定义了其余五个 Skill 的对话/Trellis 自动触发信号。
4. 五个移植 Skill 允许模型隐式调用：对话匹配触发信号时自动加载，也可用 `/skill:<name>` 显式触发。

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
- 修改任何 SKILL 或文档后运行 `tools/check-workflow.ps1`（覆盖 frontmatter、链接、自包含边界、知识条目元数据），退出码 0 才算通过。
- 新的长期边界决定按 `.agents/adr/README.md` 的生命周期入 ADR 目录；场景回归用 `tests/scenarios.md`。
新的长期边界决定按 `.agents/adr/README.md` 的生命周期入 ADR 目录；场景回归用 `tests/scenarios.md`。

## 来源与致谢

能力模式源自 `ruokee-agent-kit`（MIT）
