---
name: perf-analysis
description: 用于大模型推理性能分析与优化的证据优先工作流：基线测量、瓶颈定位、假设验证、改动对比。性能断言必须附测量环境、命令与统计口径，禁止无依据的加速倍数。
disable-model-invocation: true
---

# 性能分析（Performance Analysis）

本 Skill 用于大模型推理性能分析与优化：吞吐、延迟、显存、资源利用率、并发能力、长序列处理。模型负责主要推理；参考文档提供方法论与证据规范，不替代项目事实。

## 适用范围

覆盖五类工作：基线测量、瓶颈定位、假设验证、参数调优、改动对比评估。

边界之外：单纯的代码实现优化、产品功能定义、业务优先级判断，遵循各自常规流程。本 Skill 不做具体代码实现。项目事实来自当前代码与配置；优先级属于用户。

## 模式选择

| 模式 | 触发 | 阅读 |
| --- | --- | --- |
| 快速分析 | 默认：单一性能问题、局部调优、小 diff 自检 | `./workflow/quick-analysis.md` |
| 完整分析 | 用户显式要求「完整分析」「系统性性能审查」「全面 profiling」 | `./workflow/full-analysis.md` |
| 咨询 | 用户要讨论方案、对比工具、探索思路，无测量目标 | `./workflow/consultation.md` |

## 判断顺序

1. 识别主要关注点：吞吐、延迟、显存、利用率，还是成本。
2. 确定所处阶段：无基线 / 有基线未定位 / 已定位待验证 / 已验证待对比。
3. 按信号阅读参考文档（见下表），只读当前需要的。
4. 只报告有充分证据的结论；证据不足时输出「待验证假设」与建议采集命令。

| 信号 | 阅读 | 常配对 |
| --- | --- | --- |
| 设定性能目标、约束与权衡框架 | [analysis-thinking](./references/analysis-thinking.md) | benchmark-protocol, bottleneck-localization |
| 设计 benchmark、统计口径、A/B 对比、环境记录 | [benchmark-protocol](./references/benchmark-protocol.md) | measurement-quality |
| 测量误差来源、实验设计、显著性判断 | [measurement-quality](./references/measurement-quality.md) | benchmark-protocol, anti-patterns |
| 分层定位瓶颈、自顶向下收敛 | [bottleneck-localization](./references/bottleneck-localization.md) | profiling-evidence, analysis-thinking |
| 读取 profiler 数据、区分计算/内存/通信 | [profiling-evidence](./references/profiling-evidence.md) | bottleneck-localization |
| 显存组成、KV cache 容量估算、OOM 诊断 | [memory-and-kv-capacity](./references/memory-and-kv-capacity.md) | bottleneck-localization, quantization-evaluation |
| 吞吐延迟权衡、饱和曲线、批处理策略 | [throughput-latency-tradeoffs](./references/throughput-latency-tradeoffs.md) | analysis-thinking, bottleneck-localization |
| 量化方法、精度评估、性能收益测量 | [quantization-evaluation](./references/quantization-evaluation.md) | memory-and-kv-capacity, measurement-quality |
| 多卡并行、扩展效率、通信开销 | [multi-gpu-scaling](./references/multi-gpu-scaling.md) | bottleneck-localization, profiling-evidence |
| 常见错误做法与识别模式 | [anti-patterns](./references/anti-patterns.md) | 所有其他 references |
| 术语含义不清或不一致 | [术语表](./glossary.md) | — |

领域知识（引擎机制、参数行为、版本兼容）不在本 Skill 内维护。需要时从官方文档采集证据：① 明确来源 URL 与版本；② 访问日期；③ 标注论断类型（事实 / 推断 / 判断）；④ 版本不明时声明「需确认当前版本」。

## 证据要求

- **数字类断言的最低证据集**：① 测量环境（硬件、驱动、CUDA/框架/引擎及版本）；② 完整可复现命令；③ 负载定义（模型与精度、输入/输出 token 分布、并发或到达模型、请求数或时长、warmup、缓存状态、客户端与服务端位置）；④ 统计口径（按 benchmark-protocol 区分请求级分布与跨运行统计）；⑤ 样本数。缺任一项，该数字只能以「未完成测量」标注呈现。
- 加速倍数/提升百分比必须同时给出基线与改后的完整证据集和可复现步骤；单次运行、「理论上」、官方宣传数字（未在本机复测）都不构成有效证据，引用官方数字必须标注来源与版本并声明「未本机复测」。
- 推导结论（容量估算、延迟预测、成本推算）展示输入、公式、不确定性。
- 涉及具体引擎参数行为：版本不明时写「需确认当前使用版本」，不给确定的行为断言。
- 输出至少区分：观测（项目证据，给 `path:line`、配置键、命令输出）、推导、未验证假设、建议、用户决策。

## 授权边界

- 「分析」请求不自动授权运行有负载或影响环境的命令（benchmark、profiling、重启服务、改配置）。
- 报告写入授权与环境修改授权是两件事，分别确认。
- 只读命令（`nvidia-smi`、日志读取、配置查看）可直接执行；会改变环境或产生负载的命令先给出命令文本与预期影响，取得用户确认。

## 输出契约

- 给候选方案及各自的权衡与适用条件，不给单一答案；陈述每个判断依赖的假设。
- 性能改进建议必须包含：预期收益区间（含不确定性）、实现成本、验证方法、回退方案。
- 技术取舍转译为成本/风险/时间；优先级由用户设定。

## 停止规则

- 不为满足方法论编造发现；没有瓶颈时零发现是有效结果。
- 无基线时不推荐优化参数、不断言「XX 慢」；只能输出待验证假设与采集计划。
- 不把相似性能现象当同一瓶颈，需证明共享根因。
- 不在混合多个变量后归因单一因素；A/B 对比只改一个目标变量。
- 不把理论加速比当实测结果；不推荐未在目标环境验证的参数。
- 不报告 profiler 能机械生成的原始 trace；提炼关键瓶颈与方向。
- 只读与咨询任务不修改被审查文件；写入测量报告的既有授权仍然适用。
