---
name: inference-stack
description: 大模型推理技术栈知识库的建库与维护规则。叶子文档由用户在具体场景中按来源分级与快照流程采集并沉淀；Agent 触发本 Skill 时执行建库/复核合同，不凭记忆生成引擎事实。
---

# 推理技术栈知识库（Inference Stack）

大模型推理领域的**个人知识库**：vLLM、TensorRT-LLM、SGLang 等引擎，量化、KV cache、批处理、并行等优化技术，CUDA/驱动兼容，容器与编排部署。

**本 Skill 不凭记忆生成引擎事实。** 它定义知识条目的准入标准、格式与维护规则；具体内容由具体场景驱动、按以下采集规则写入叶子文档：① 来源分级（一手来源 > 二手来源 > 仅作线索）；② 保存来源快照（URL + 访问日期 + 版本）；③ 论断分类（事实 / 推断 / 判断 / 宣传 / 未解决）；④ 版本敏感内容标注适用版本。未入库的问题先现场调研，结果值得复用时再入库。

## 建库规则（每条知识必须满足）

每个叶子文档头部携带审计元数据：

```markdown
---
source: <官方文档URL / 论文 / 仓库>
version: <适用版本或 commit；不确定写「版本未确认」>
accessed: <访问日期>
last_reviewed: <最后复核日期>
status: current | needs-review | expired
---
```

- 内容只能来自一手来源（官方文档、论文、源码）或标注分级的二手来源；每条版本敏感论断标注适用版本。
- 版本无法确认时该条目 status 必须是 `needs-review`，且不得被其他工作流当作确定事实引用。
- 引擎大版本发布后，相关条目标记 `needs-review`；复核通过改回 `current` 并更新 `last_reviewed`。
- 条目过期（来源已失效且无法复核）标记 `expired` 保留历史，或删除。

## 目录规划

```
references/
├── README.md            本文件：建库协议与条目模板
├── engines/             各引擎：overview / parameters / troubleshoot
├── optimization/        量化 / kv-cache / attention / batching
├── hardware/            gpu-arch / cuda 兼容 / multi-gpu
├── deployment/          容器 / 编排
└── patterns/            oom / startup-failure / slow-inference / dependency-conflict
```

**当前状态：条目尚未建设。** 首批条目由实际使用场景驱动产生（例：第一次排查某引擎启动失败 → 采集官方排障文档快照 → 沉淀 `engines/<engine>/troubleshoot.md` 首版）。不预生成空壳。

## 使用方式

- 用户显式要求「查知识库 / 这个问题以前查过吗」时，Agent 按问题信号路由到对应子目录，只读存在的条目；命中条目时连同其 status 与 version 一并报告——`needs-review` 的条目必须提示复核。
- 未命中就明说「未入库」，并从官方文档现场调研，询问是否将结果沉淀为新条目。

## 停止规则

- 不凭记忆填充引擎参数、兼容矩阵、性能数字。
- 不把 `needs-review` / `expired` 条目当确定事实输出。
- 不批量预生成条目；一场景一条目。
- 本 Skill 不做分析判断，只提供带审计信息的知识。
