# 个人 AI 工作流（推理优化 × 部署排障）

为「大模型推理优化 + 部署问题排查」方向定制的防幻觉 AI 工作区。核心理念：**证据优先、事实与推断分离、版本敏感断言必须可审计**。能力模式取自 ruokee-agent-kit（信号路由、停止规则、事实-only 报告、来源快照），经 claude 设计、codex 独立验证（7 项必须修正已全部落实，见 `_pipeline/04-codex-verification.md`）；后经第二轮闭环补强：codex 差异清单（`_pipeline/05-codex-diff.md`）→ claude 落地 P0-P5（`_pipeline/06-claude-implementation.md`）→ omp 终检。

## 目录

```
workflow/
├── README.md            本文件
├── AGENTS.md            工作区 Agent 规则（证据纪律、授权分级、存储约定）
├── DECISIONS.md         设计决定记录（背景/决定/替代项/后果/重审条件）
├── skills/              五个 Skill（OMP 加载，见 omp/setup.md）
│   ├── perf-analysis/       推理性能分析（用户触发，3 模式 + benchmark 协议 + 10 篇方法论文档）
│   ├── deploy-troubleshoot/ 部署排障（用户触发，2 模式 + 环境快照标准 + 9 篇方法论文档）
│   ├── issue-report/        事实-only 问题报告（用户触发）
│   ├── tech-research/       证据优先调研/学习报告（用户触发）
│   └── inference-stack/     推理知识库建库规则（Agent 触发，条目场景驱动生成）
├── reports/             问题报告存储（YYYY-MM-DD-NN-theme.md）
├── omp/                 OMP 落地：setup.md（安装+版本探测）、prompts/（可复用模式索引 + 独立 prompt）
├── tests/               回归场景卡（scenarios.md）与 OMP 加载自检步骤（omp-loading.md）
├── tools/               check-workflow.ps1 结构/链接/自包含自动检查
└── _pipeline/           构建过程材料（总结/设计/验证，只读归档）
```

## 快速开始

1. 按 [omp/setup.md](./omp/setup.md) 挂载 Skill 目录（配置键 `skills.customDirectories`，已在 OMP 18.2.3 验证）。
2. 重启 OMP，用 `/skill:perf-analysis`、`/skill:deploy-troubleshoot`、`/skill:issue-report`、`/skill:tech-research` 触发。
3. 在本目录工作时 [AGENTS.md](./AGENTS.md) 的规则自动生效。

## 防幻觉机制一览

| 机制 | 落点 |
| --- | --- |
| 数字断言最低证据集（环境+命令+负载+统计+样本数） | perf-analysis `references/benchmark-protocol.md` |
| 请求级分布 vs 跨运行统计分开；改进小于波动不称提升 | 同上 §3 |
| A/B 单变量原则，混杂因素必列 | 同上 §5 |
| 命令五元组（文本/退出码/stdout/stderr/位置）与脱敏 | deploy-troubleshoot `references/environment-snapshot.md` |
| 命令分级 L0-L3；「排查」≠授权改环境 | deploy-troubleshoot SKILL.md、AGENTS.md |
| 根因需反向验证；未验证只能是「最可能原因」 | deploy-troubleshoot `workflow/full-troubleshoot.md` |
| 事实-only 报告，禁止定位/方案混入 | issue-report SKILL.md、reports/ |
| 论断五分类（事实/推断/判断/宣传/未解决） | tech-research SKILL.md |
| 来源快照审计链（原文/摘要+URL+作者+日期） | tech-research SKILL.md |
| 知识条目审计元数据（source/version/status） | inference-stack SKILL.md |
| 版本不明 → 「需确认当前版本」，不给行为断言 | 所有 SKILL + AGENTS.md |
| 零发现合法；不编造凑数 | 各 SKILL 停止规则 |

## 多代理闭环（herdr 可用时）

```
用户需求
  → claude（study:p2）：按 Skill 设计方案/报告
  → codex（study:p3）：独立验证（只读，PASS/FAIL + 证据 + 必须修正项）
  → omp（study:p1）：修正落地执行（L2/L3 命令另行授权）
  → 产出归档（reports/ 调研目录）；可复用模式沉淀 omp/prompts/
```

- 前置探测：`test "$HERDR_ENV" = 1`；herdr 不可用时单代理照常。
- 设计稿与验证报告分别落盘（如 `_pipeline/` 模式），验证只读不改。
- 本工作区即由该闭环构建：01 总结(omp) → 03 设计(claude) → 04 验证(codex) → 落地(omp)。

## 维护

- `inference-stack` 条目按需生成（一场景一条目），引擎大版本发布后标 `needs-review` 复核。
- 报告解决后从 `reports/` 删除或移入对应任务材料。
- OMP 升级后重验 `skills.customDirectories`（`omp config get ... --json`），不猜键名。
- 修改任何 SKILL 或文档后运行 `tools/check-workflow.ps1`（覆盖 frontmatter、链接、自包含边界、知识条目元数据），退出码 0 才算通过。
- 新的长期边界决定记入 `DECISIONS.md`；场景回归用 `tests/scenarios.md`。

## 来源与致谢

能力模式源自对 `C:/Users/admin/Desktop/study/工作/ruokee-agent-kit`（MIT）的通读，过程材料完整保留在 `_pipeline/`。
