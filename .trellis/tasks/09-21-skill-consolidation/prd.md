# 整合 5 个 Skill 为 inference-ops

## Goal

将 perf-analysis、deploy-troubleshoot、issue-report、tech-research、inference-stack 五个 Skill 整合为单一 `inference-ops` Skill。动机：原拆分过细，不符合「个人 Agent Kit」的精简初衷；一个 Skill 覆盖「大模型推理系统的部署排障 × 性能优化」完整域。

## Requirements

### 新 Skill 结构（自包含，用户触发型）

```
skills/inference-ops/
├── SKILL.md                统一入口：域定义、模式路由、证据纪律、授权 L0-L3、停止规则
├── workflow/
│   ├── quick.md            ← quick-troubleshoot + quick-analysis（默认模式，故障/性能双轨）
│   ├── full.md             ← full-troubleshoot + full-analysis（重型闭环，双轨）
│   └── consult.md          ← consultation + tech-research 流程（咨询/调研双轨）
├── references/             19+1 篇 → 10 篇（见映射表）
├── glossary.md             ← perf + deploy 两术语表合并
└── agents/openai.yaml      用户触发型必需
```

### references 映射（内容不丢失，仅重组）

| 新文件 | 来源 |
| --- | --- |
| evidence-and-snapshot.md | deploy: evidence-collection + environment-snapshot |
| reporting.md | issue-report 全部 + tech-research 的来源分级/论断分类/快照审计链/输出骨架 |
| layered-diagnosis.md | deploy: layered-diagnosis + reproduction-and-bisect + resolution-rollback-and-closure |
| deploy-common-causes.md | deploy: dependency-and-runtime-boundaries + container-network-permission + resource-exhaustion |
| benchmark-protocol.md | perf: benchmark-protocol + measurement-quality |
| bottleneck-localization.md | perf: bottleneck-localization + profiling-evidence |
| perf-topics.md | perf: throughput-latency-tradeoffs + memory-and-kv-capacity + quantization-evaluation + multi-gpu-scaling |
| analysis-thinking.md | perf: analysis-thinking（保留，更新交叉引用） |
| anti-patterns.md | perf + deploy 两份 anti-patterns 合并 |
| knowledge-base.md | inference-stack SKILL + 其 references/README.md（建库协议、审计元数据、条目模板） |

### 清理与同步

- 删除旧 5 个 Skill 目录（git 450da23 可恢复，用户已确认）。
- 同步引用：README.md、AGENTS.md、omp/setup.md、omp/prompts/design-verify-execute.md、omp/prompts/README.md、tests/scenarios.md、tests/omp-loading.md、reports/README.md。
- tools/check-workflow.ps1：`$allSkills` 改为 `@('inference-ops')`；第 4 节知识条目检查改指向 `inference-ops` 的知识条目目录。
- DECISIONS.md 追加「单 Skill 整合」决定（不改历史条目）。
- OMP `skills.customDirectories` 仍指向 `skills/` 目录，无需变更。

## Acceptance Criteria

- [x] `skills/` 下仅 `inference-ops` 一个目录，结构完整（SKILL.md frontmatter、agents/openai.yaml、workflow、references、glossary）
- [x] 19+1 篇旧 references 的实质内容全部映射进新 references（重组而非删减）
- [x] `tools/check-workflow.ps1` 更新后全项 PASS、退出码 0
- [x] 全仓库无旧 Skill 名残留引用（grep 验证；git 历史/.trellis 任务材料除外；DECISIONS.md 历史与新决定条目按设计保留旧名）
- [x] tests/scenarios.md 8 个场景卡改写为 inference-ops 口径，边界语义不变

## Notes

- 用户决策（2026-09-21）：全部 5 合 1；命名 inference-ops；旧目录直接删除；本轮不含 ruokee 式完整仓库骨架重构。
