# Profiling 证据

如何读取 profiler 数据、区分排队/计算/内存/通信、避免把工具伪影当真实瓶颈。

## 适用信号

- 需要算子/内核级定位
- 怀疑计算效率、内存带宽、kernel launch 开销
- 审查他人给出的 profiling 结论

## Profiling 概念层（版本无关）

### 时间分类

**排队等待（Queue Time）**：请求已到达但未开始处理，在调度器队列中。

**CPU 提交（Host Time）**：主机端准备数据、组 batch、下发 kernel。

**GPU 执行（Device Time）**：kernel 在 GPU 上执行。

**空洞（Idle Gap）**：GPU 在等待下一个 kernel，可能是 CPU 提交慢或同步点。

**通信（Communication）**：多卡间数据传输（NVLink/PCIe）。

**判断**：
- 排队占比高 → 调度瓶颈或批处理慢
- CPU 提交占比高 → 框架开销或数据预处理
- 空洞多 → kernel launch 开销、过度同步、CPU-GPU 流水线断裂
- GPU 执行占比高且利用率高 → 真实计算瓶颈
- 通信占比高 → 多卡并行效率低

### 计算 vs 访存

**计算受限（Compute-bound）**：
- SM 利用率高（>80%）
- 内存带宽利用率低（<50%）
- 算术强度（FLOP/Byte）高
- 优化方向：算子融合、降低精度、更快 GPU

**访存受限（Memory-bound）**：
- 内存带宽利用率高（>70%）
- SM 利用率低或中等
- 算术强度低
- 优化方向：量化、减少冗余访存、Tensor Core

**混合**：两者都不饱和 → 查 kernel 效率、warp 占用率、bank conflict

## 工具选择（按实际版本查官方文档）

### nsys（Nsight Systems）

**用途**：系统级时间线，看整体流水线、CPU-GPU 交互、kernel 序列。

**关键视图**：
- Timeline：横向时间轴，看排队、空洞、kernel 重叠
- CUDA API：看 kernel launch 频率与参数
- GPU Utilization：整体利用率曲线

**适合**：找排队、空洞、调度问题、多卡通信。

**命令示例**（版本相关，以当前版本为准）：
```bash
nsys profile --trace=cuda,nvtx,osrt --output=report.qdrep python script.py
```

### ncu（Nsight Compute）

**用途**：单 kernel 详细分析，看 SM 利用率、带宽、warp 调度、指令组成。

**关键指标**：
- SM%：Streaming Multiprocessor 利用率
- Memory Throughput：实际 vs 峰值带宽
- Compute Throughput：实际 vs 峰值 FLOPS
- Warp Occupancy：并行度

**适合**：定位单一 kernel 的计算/内存瓶颈。

**命令示例**（版本相关，以当前版本为准）：
```bash
ncu --set full --target-processes all python script.py
```

**注意**：ncu 开销极大，只 profile 目标 kernel，不用于端到端测量。

### 引擎自带 profiler

**vLLM**：`--enable-profiler`，输出 Chrome trace JSON，含调度、prefill/decode、KV cache 事件。

**TensorRT-LLM**：`trtllm-build --profiling`，Layer timing report。

**优点**：框架语义清晰（知道哪个是 Attention、哪个是 MLP），无需映射 kernel 名。

**缺点**：粒度较粗，不到 kernel/指令级。

**使用**：先用引擎 profiler 找慢的 layer/phase，再用 ncu 深挖具体 kernel。

## Profiling 证据的解读

### 证据能证明什么

**可直接读出**：
- 某 kernel 占总执行时间 X%
- GPU 整体利用率 Y%
- 内存带宽达峰值的 Z%

**可推导**：
- kernel A 是瓶颈（占比高 + 无优化空间时）
- 访存受限（带宽饱和 + SM 利用率中等）

### 证据不能证明什么

**不能直接断言**：
- 「kernel A 效率低」→ 需要与理论峰值或同类 kernel 对比
- 「GPU 利用率低就是代码问题」→ 可能是 batch size 小、调度慢、输入瓶颈

**需要配合其他证据**：
- 单看 SM 利用率不够，要结合带宽、occupancy、指令 mix
- 单看某 kernel 慢不够，要看是否在关键路径、占比多少

## 常见误判

### 1. Profiler 自身开销

**现象**：开 profiler 后性能下降 2-10 倍。

**原因**：
- nsys 抓所有 API 调用，有开销但通常<10%
- ncu 重跑 kernel 多次收集指标，开销巨大（10 倍+）
- 框架 profiler 打点、序列化 trace

**处理**：
- 性能数字用不开 profiler 的测量
- profiler 只用于定位，不用于绝对性能
- 报告时声明「profiling 模式」

### 2. 采样不代表稳态

**现象**：profiler 抓前 100 个请求，包含大量 warmup。

**处理**：warmup 后再开始 profiling，或在 trace 里手动剔除 warmup 段。

### 3. 把 kernel 名当证据

**现象**：「`kernel_123` 占 50% 时间，它是瓶颈」。

**问题**：不知道这个 kernel 做什么、该有多快。

**处理**：
- 映射 kernel 到算子（Attention/MLP/LayerNorm）
- 对比该 kernel 的实际性能与理论峰值
- 检查是否因 batch size 小导致效率低

### 4. 忽略多卡通信

**现象**：单卡 profile 看起来好，多卡吞吐不成比例增长。

**原因**：通信时间未计入，或通信与计算未重叠。

**处理**：用 nsys 看多卡 timeline，检查 AllReduce/AllGather 时间与重叠度。

## 正反例

### 好的 profiling 报告

```
环境：A100-80GB，vLLM 0.4.2，Llama-2-7B-FP16，batch=16
工具：nsys 2024.1.1
采集：warmup 50 请求后，profiling 100 个 decode step

发现：
1. Attention kernel 占总 GPU 时间 65%
   - Flash Attention 2 实现
   - 内存带宽利用率 78%（接近峰值 80%）
   - SM 利用率 45%（访存受限，符合预期）
   → 结论：Attention 是瓶颈但已接近理论极限，优化空间有限
   
2. GPU 空洞占 15%
   - 空洞出现在 decode step 间
   - CPU 侧调度耗时 2-3ms
   → 结论：调度可优化，但非主要瓶颈（15% vs 65%）
```

具体、可验证、给工具版本、区分瓶颈与优化空间。

### 坏的 profiling 声明

```
「profiling 显示 Attention 慢，优化后快了 2 倍」

问题：
- 未说 profiling 工具与版本
- 未说 Attention 占比
- 未说如何判断「慢」（与什么对比）
- 2 倍提升未给基线环境与测量方法
```

## 停止规则

**足够定位**：找到占比 >30% 的热点且知道对应算子/phase。

**需要深挖**：热点 kernel 内部需要 ncu 看指令级。

**不需要 profiling**：
- 服务级已明确瓶颈（调度、batch size、资源配置）
- GPU 利用率已饱和且吞吐符合预期

## 与其他文档关系

- bottleneck-localization.md：定位方法，profiling 是其中一层工具
- memory-and-kv-capacity.md：显存分析需要 profiling 看实际占用
- anti-patterns.md：profiling 常见误用
