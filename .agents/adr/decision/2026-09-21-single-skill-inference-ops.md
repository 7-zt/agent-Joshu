# ADR 决定：单 Skill 整合（inference-ops）

## 背景

初版按能力拆成 5 个 Skill（perf-analysis、deploy-troubleshoot、issue-report、tech-research、inference-stack）。实际使用中拆分过细：五个入口共享同一批纪律（证据、授权、版本、停止规则），维护成本高于收益，不符合个人 Agent Kit 的精简初衷。

## 决定

整合为单一 `inference-ops` Skill（部署排障 × 性能优化，报告/调研/知识沉淀作为输出形态），三模式（quick/full/consult）双轨（故障/性能）。19+1 篇 references 重组为 10 篇，方法论内容不删减。

## 真实替代项

- 保持 5 Skill 拆分（入口语义更专，但纪律重复、加载面大）
- 合成 2 Skill（排障 + 性能；报告/调研归属仍尴尬）

## 后果

- ✓ 单入口覆盖完整域；共享纪律只维护一份
- ✓ OMP 加载与触发更简单
- ✗ SKILL.md 模式路由变重；单目录丢失影响面变大（git 可恢复）

## 重审条件

域明显扩张（如训练侧运维）导致单 Skill 过大时。
