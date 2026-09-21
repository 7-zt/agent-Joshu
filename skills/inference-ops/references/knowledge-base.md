# 知识库

大模型推理技术栈的**个人知识库**建库协议：vLLM、TensorRT-LLM、SGLang 等引擎，量化、KV cache、批处理、并行等优化技术，CUDA/驱动兼容，容器与编排部署。

**本协议下不凭记忆生成引擎事实。** 这里只定义知识条目的准入标准、格式与维护规则；具体内容由具体场景驱动、按采集规则写入叶子文档：① 来源分级（一手来源 > 二手来源 > 仅作线索）；② 保存来源快照（URL + 访问日期 + 版本）；③ 论断分类（事实 / 推断 / 判断 / 宣传 / 未解决）；④ 版本敏感内容标注适用版本。未入库的问题先现场调研（调研流程见 workflow/consult.md 调研轨），结果值得复用时再入库。

## 条目存放与目录规划

知识条目存放于本目录的 `knowledge/` 子目录：

```text
references/knowledge/
├── engines/             各引擎：overview / parameters / troubleshoot
├── optimization/        量化 / kv-cache / attention / batching
├── hardware/            gpu-arch / cuda 兼容 / multi-gpu
├── deployment/          容器 / 编排
└── patterns/            oom / startup-failure / slow-inference / dependency-conflict
```

**当前状态：条目尚未建设。** 首批条目由实际使用场景驱动产生（例：第一次排查某引擎启动失败 → 采集官方排障文档快照 → 沉淀 `engines/<engine>/troubleshoot.md` 首版）。不预生成空壳。

## 条目模板

```markdown
---
source: <官方文档URL / 论文 / 仓库链接，多个则列表>
version: <适用版本或 commit；不确定写「版本未确认」>
accessed: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
status: current
---

# <主题>

<正文。每条版本敏感论断标注适用版本；
引用官方文档时给文档版本/页面；二级结论标注 [事实]/[推断]/[判断]>

## 复核记录

- YYYY-MM-DD: 复核结论（仍有效 / 需更新的原因）
```

## 建库规则（每条知识必须满足）

- 每个叶子文档头部携带审计元数据（source / version / accessed / last_reviewed / status）。
- 内容只能来自一手来源（官方文档、论文、源码）或标注分级的二手来源；每条版本敏感论断标注适用版本。
- 版本无法确认时该条目 status 必须是 `needs-review`，且不得被其他工作流当作确定事实引用。
- 引擎大版本发布后，相关条目标记 `needs-review`；复核通过改回 `current` 并更新 `last_reviewed`。
- 新条目由实际场景驱动（排查/调优/调研中采集），按来源分级与快照流程产出，用户确认后入库。
- 更新条目追加「复核记录」，不删除历史。
- 一场景一条目；不批量预填、不设数量目标。

## 状态流转

- `current`：来源可查、版本确认、近期复核过。可被其他工作流引用。
- `needs-review`：引擎大版本发布、来源改版、或版本未确认。引用时必须提示复核。
- `expired`：来源失效且无法复核。保留作历史，或删除。

## 使用方式

- 用户显式要求「查知识库 / 这个问题以前查过吗」时，按问题信号路由到对应子目录，只读存在的条目；命中条目时连同其 status 与 version 一并报告——`needs-review` 的条目必须提示复核。
- 未命中就明说「未入库」，并从官方文档现场调研，询问是否将结果沉淀为新条目。

## 停止规则

- 不凭记忆填充引擎参数、兼容矩阵、性能数字。
- 不把 `needs-review` / `expired` 条目当确定事实输出。
- 不批量预生成条目；一场景一条目。
- 知识库只提供带审计信息的知识，分析判断由工作流模式完成。

## 与其他文档关系

- [reporting](./reporting.md)：来源分级、快照、论断分类的完整规则
- [evidence-and-snapshot](./evidence-and-snapshot.md)：环境事实采集标准
