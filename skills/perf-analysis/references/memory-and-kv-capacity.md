# 显存与 KV Cache 容量

显存组成、容量估算公式、KV cache 管理策略、OOM 诊断。

## 显存组成

总显存 = 模型权重 + KV cache + 激活值 + 临时缓冲 + 框架开销

**模型权重**：
- FP16: 每参数 2 字节
- INT8: 每参数 1 字节  
- INT4: 每参数 0.5 字节
- 7B 模型 FP16 ≈ 14GB

**KV cache**（推理主要消耗）：
- 每 token 每层：2 × hidden_size × 数据类型字节数
  （以上为标准多头注意力 MHA 的情形；GQA/MQA 下为 2 × num_kv_heads × head_dim × 字节数，
  num_kv_heads 小于注意力头数时显存占用相应降低，估算前先确认模型的 KV 头数配置）
- 7B 模型（32 层，hidden 4096）FP16：
  - 单 token: 2 × 32 × 4096 × 2 = 524KB
  - 2048 token: 约 1GB
  - batch 16: 约 16GB

**激活值**：prefill 时较大，decode 时小（只算当前 token）。

**估算公式**：

```
显存需求 ≈ 模型权重 + batch_size × max_seq_len × kv_per_token
```

## KV Cache 管理策略

### PagedAttention（vLLM）

- KV cache 分页管理，类似虚拟内存
- 减少碎片，支持更大 batch
- 动态分配，共享 prefix

### 优先级淘汰

- LRU: 最久未用先淘汰
- 频率: 低频先淘汰
- 重计算代价: 便宜的先淘汰

### Prefix caching

- 系统 prompt 共享
- 文档检索后的 context 共享

## OOM 诊断

**信号**：
- CUDA out of memory
- 服务拒绝新请求
- 吞吐随 batch 增长突然断崖

**定位**：
1. 检查实际显存使用（`nvidia-smi`）
2. 估算理论需求（上述公式）
3. 比较差异，找未预期的大头

**常见原因**：
- batch size 或 max tokens 配置过大
- KV cache 预分配过多
- 多个模型同时加载
- 显存碎片

**解决方向**：
- 降低 batch size
- 限制 max_seq_len
- 启用 KV cache 淘汰
- 量化模型

## 与其他文档关系

- bottleneck-localization.md：显存瓶颈定位
- quantization-evaluation.md：量化减少显存
