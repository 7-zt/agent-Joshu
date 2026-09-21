# 性能专题

四个高频优化专题的领域方法：吞吐延迟权衡、显存与 KV cache、量化评估、多卡并行。设定目标与约束的框架见 [analysis-thinking](./analysis-thinking.md)；测量标准见 [benchmark-protocol](./benchmark-protocol.md)。

## 一、吞吐延迟权衡

### 核心概念

**吞吐（Throughput）**：单位时间处理量（tokens/s, requests/s）。**延迟（Latency）**：单个请求从提交到完成的时间。**关系**：通过批处理和并发提高吞吐，但延迟会增加（排队等待）。

### 饱和曲线

```text
吞吐
  ^     /----- 饱和
  |    /
  |   /
  |  /  线性增长区
  | /
  +----------> 并发/batch size
```

**线性区**：增加并发，吞吐线性增长，延迟稳定。**饱和区**：资源用尽，吞吐平台，延迟急剧增加。**拐点**：最佳工作点（高吞吐 + 可接受延迟）。

### 批处理策略

- **Static batching**：固定 batch size，等待凑满才处理；低负载时延迟高。
- **Dynamic batching**：等待超时或凑满，先到先处理；平衡延迟与吞吐。
- **Continuous batching**（如 vLLM）：每个 token 独立调度，decode 完成立即释放、新请求插入；最大化 GPU 利用率。

### 权衡决策

**延迟敏感**（交互场景）：小 batch、短超时、预留容量应对尖峰。**吞吐优先**（批处理）：大 batch、长超时凑批、饱和运行。

## 二、显存与 KV cache 容量

### 显存组成

总显存 = 模型权重 + KV cache + 激活值 + 临时缓冲 + 框架开销

**模型权重**：FP16 每参数 2 字节；INT8 每参数 1 字节；INT4 每参数 0.5 字节。7B 模型 FP16 ≈ 14GB。

**KV cache**（推理主要消耗）：

- 每 token 每层（标准多头注意力 MHA）：2 × hidden_size × 数据类型字节数。
- GQA/MQA 下为 2 × num_kv_heads × head_dim × 字节数；num_kv_heads 小于注意力头数时显存占用相应降低，估算前先确认模型的 KV 头数配置。
- 7B 模型（32 层，hidden 4096）FP16：单 token 2 × 32 × 4096 × 2 = 524KB；2048 token 约 1GB；batch 16 约 16GB。

**激活值**：prefill 时较大，decode 时小（只算当前 token）。

**估算公式**：

```text
显存需求 ≈ 模型权重 + batch_size × max_seq_len × kv_per_token
```

### KV cache 管理策略

- **PagedAttention**（vLLM）：KV cache 分页管理（类似虚拟内存），减少碎片，支持更大 batch，动态分配，共享 prefix。
- **优先级淘汰**：LRU / 低频先淘汰 / 重计算代价便宜的先淘汰。
- **Prefix caching**：系统 prompt 共享；文档检索后的 context 共享。

### OOM 诊断

**信号**：CUDA out of memory；服务拒绝新请求；吞吐随 batch 增长突然断崖。

**定位**：检查实际显存使用（`nvidia-smi`）→ 估算理论需求（上述公式）→ 比较差异，找未预期的大头。

**常见原因**：batch size 或 max tokens 配置过大；KV cache 预分配过多；多个模型同时加载；显存碎片。

**解决方向**：降低 batch size；限制 max_seq_len；启用 KV cache 淘汰；量化模型。

## 三、量化评估

### 量化方法

- **INT8**：8 位整数，典型 2 倍显存减少，1.5-2 倍加速。
- **INT4/GPTQ/AWQ**：4 位，4 倍显存减少，2-3 倍加速，需校准数据。
- **FP8**：8 位浮点，硬件支持时效率高（H100）。

以上收益数字为典型区间，实际以本机测量为准（benchmark-protocol）。

### 精度评估

**不能只看 perplexity**：PPL 是平均指标，掩盖局部退化；某些任务（推理、代码）对量化敏感。

**推荐评估**：下游任务准确率（MMLU、HumanEval 等）；对比 FP16 baseline；多个数据集，找最敏感的。

**评估设计**：固定随机种子；相同 prompt 与生成参数；至少 500 样本；报告均值与置信区间。

### 性能收益测量

**需要测量**：吞吐提升（同负载下）；延迟降低（单请求）；显存减少（实际值，不只是理论）；batch size 增加空间。

**对比方法**：环境固定；只改量化方法；warmup 后测稳态。

### 权衡决策

**可接受量化**：任务准确率下降 <2%；性能提升 >30%；显存减少支持更大 batch。

**不推荐量化**：准确率下降 >5%；性能提升 <15%（不值得维护复杂度）；下游任务对精度极敏感（医疗、金融）。

## 四、多卡并行与扩展

### 并行策略

- **张量并行（Tensor Parallelism）**：单层权重切分到多卡；每个 token 都需要通信（AllReduce）；适合单机多卡、NVLink 高带宽。
- **流水线并行（Pipeline Parallelism）**：层切分到多卡，micro-batch 流水；通信少，但有 bubble（空闲）。
- **数据并行（Data Parallelism）**：完整模型复制到每卡，批次切分；推理时少用（显存浪费）。

### 扩展效率

**理想扩展**：N 卡吞吐 = 单卡 × N。**实际**：效率 = 实际吞吐 / (单卡吞吐 × N)。

**典型值**：2 卡 85-95%；4 卡 75-90%；8 卡 60-80%。

**损失来源**：通信时间、负载不均、同步开销、流水线 bubble。

### 通信分析

**工具**：nsys 看 NCCL 调用、NVLink 利用率。**指标**：通信时间占比；通信与计算重叠度；带宽利用率。**优化**：通信计算重叠（异步）；减少同步点。

### 判断何时并行

**需要并行**：模型太大单卡装不下；单卡吞吐不够。**不需要并行**：显存够用；单卡已满足需求；通信开销 >20%（跨机）。

## 与其他文档关系

- [bottleneck-localization](./bottleneck-localization.md)：定位显存/通信瓶颈的方法
- [benchmark-protocol](./benchmark-protocol.md)：所有收益数字的测量标准
- [analysis-thinking](./analysis-thinking.md)：目标与约束的权衡框架
