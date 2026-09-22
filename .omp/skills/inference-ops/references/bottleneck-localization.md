# 瓶颈定位与 Profiling 证据

分层收敛定位性能瓶颈的方法，与配套的 profiler 数据解读规范。第一部分是定位路径；第二部分是算子/内核级的证据解读。核心纪律：自顶向下、信号驱动、假设验证、停止条件明确。

## 一、分层定位方法

### 适用信号

- 有基线但不知道瓶颈在哪
- 优化后需验证是否命中真正瓶颈
- 多个候选瓶颈需排序

### 自顶向下分层

```
服务级（吞吐/延迟形态）
  ↓ 信号指向
引擎级（调度/批处理/队列/缓存）
  ↓ 信号指向
算子/内核级（计算/内存/通信）
  ↓ 信号指向
资源级（利用率/带宽/功耗）
```

**只在上层证据指向下层时才下探**，不做无目标的全量 profiling。

### 四层模型

**服务级**：

- 信号：延迟 P50/P95/P99 分布与长尾；吞吐饱和曲线（并发增加时吞吐变化）；错误率（超时、OOM、拒绝）。
- 判断：吞吐随并发线性增长后平台 → 找平台原因（计算饱和/队列满/资源耗尽）；延迟长尾（P99 >> P50）→ 找长尾原因（GC/调度抖动/队列积压）；低并发已饱和 → 串行瓶颈或配置过保守。
- 下探条件：形态异常或未达预期。

**引擎级**（信号以 vLLM 为例）：

- 信号：调度（等待队列长度、批组成延迟）；批处理（实际 batch size、序列数、padding 率）；KV cache（命中率、换入换出、碎片）；迭代时间（prefill vs decode 占比）。
- 判断：等待队列长但 GPU 利用率低 → 调度策略或批组成逻辑；batch size 远小于配置 → 请求到达率低或序列长度超限；KV cache 频繁换出 → 显存不足或缓存策略。
- 下探条件：引擎指标正常但吞吐仍低。

**算子/内核级**（需 profiler，解读见第二部分）：

- 信号：时间占比、GPU 占用（SM 利用率、Tensor Core 利用率）、内存带宽（实际 vs 峰值）、算子融合（多余拷贝或小 kernel）。
- 判断：单一算子占 >50% 时间 → 该算子是瓶颈；SM 利用率低但带宽高 → 访存受限；SM 利用率高但带宽低 → 计算受限；大量小 kernel 且间隔 → kernel launch 开销或算子未融合。

**资源级**：

- 信号：GPU 利用率（`nvidia-smi` 的 GPU-Util）、显存带宽（DRAM read/write throughput）、功耗与温度、PCIe/NVLink 带宽（多卡）。
- 判断：GPU 利用率 <70% 且无等待 → 框架调度或主机端瓶颈；显存带宽饱和（>80% 峰值）→ 访存受限，考虑量化或算子优化；温度接近阈值 → 热节流；PCIe 带宽饱和 → 模型加载或多卡通信瓶颈。
- 停止：资源级是最底层，找到瓶颈资源后向上推导优化方向。

### 每层四问

1. 该层指标在期望范围吗？（与理论峰值、同类系统、历史基线对比）
2. 该层有明显异常信号吗？（抖动、长尾、空洞）
3. 该层信号指向哪个下层？（计算/内存/调度/通信）
4. 改善该层需要哪个上层配合？（参数/负载/架构）

### 证据边界

**可直接得出**：某层指标实测值（吞吐 X tok/s、GPU 利用率 Y%）；某算子占比（Attention 占 60% 时间）。

**需验证假设**：「该层是瓶颈」→ 针对性优化后是否改善；「某参数过小」→ 调整后是否消除瓶颈。

**需审计链**：理论峰值（FLOPS、带宽）→ 引用 GPU 规格与来源；框架能达到的实际峰值 → 引用官方 benchmark 或自测。

### 正反例

**好的定位过程**：

```text
观测：并发 32 时吞吐 100 tok/s，GPU 利用率 50%
↓ 服务级：吞吐未饱和且利用率低，下探引擎级
观测：vLLM 实际 batch size 平均 8，配置是 256
↓ 引擎级：batch 未打满，检查原因
观测：请求到达率低（每秒 10 个），序列长度正常
↓ 结论：非性能瓶颈，是负载不足。饱和测试需要更高并发
```

逐层验证，发现真正原因（负载不足而非性能问题）。

**坏的定位**：「GPU 利用率只有 60%，肯定是代码效率低」→ 未检查是调度问题、batch size 配置、还是输入端瓶颈 → 直接优化算子，浪费时间。跳过分层，直接猜结论。

### 常见误判

1. GPU 利用率当唯一指标：利用率低可能是调度、batch size、队列空，不一定是计算慢。
2. 单层优化未看上下文：优化算子但 batch size 过小，优化无效。
3. 不验证假设就下结论：看到 KV cache 换出就断言显存不足，未检查是否缓存策略可调。
4. 混淆瓶颈与优化空间：找到瓶颈不代表能优化（理论极限）。

### 停止条件

- **找到瓶颈**：某层指标达理论极限（带宽 >90% 峰值、SM 利用率 >85%）。
- **找到配置问题**：某层指标远低于应有水平，且有明确配置/参数可调。
- **需要架构改动**：瓶颈需要改模型结构、换引擎、换硬件才能解决，超出调优范围。
- **达到足够好**：性能满足目标，无需继续定位。

## 二、Profiling 证据

### 概念层（版本无关）

**时间分类**：

- **排队等待（Queue Time）**：请求已到达但未开始处理，在调度器队列中。
- **CPU 提交（Host Time）**：主机端准备数据、组 batch、下发 kernel。
- **GPU 执行（Device Time）**：kernel 在 GPU 上执行。
- **空洞（Idle Gap）**：GPU 在等待下一个 kernel，可能是 CPU 提交慢或同步点。
- **通信（Communication）**：多卡间数据传输（NVLink/PCIe）。

**判断**：排队占比高 → 调度瓶颈或批处理慢；CPU 提交占比高 → 框架开销或数据预处理；空洞多 → kernel launch 开销、过度同步、CPU-GPU 流水线断裂；GPU 执行占比高且利用率高 → 真实计算瓶颈；通信占比高 → 多卡并行效率低。

**计算 vs 访存**：

- **计算受限（Compute-bound）**：SM 利用率高（>80%）、内存带宽利用率低（<50%）、算术强度（FLOP/Byte）高。优化方向：算子融合、降低精度、更快 GPU。
- **访存受限（Memory-bound）**：内存带宽利用率高（>70%）、SM 利用率低或中等、算术强度低。优化方向：量化、减少冗余访存、Tensor Core。
- **混合**：两者都不饱和 → 查 kernel 效率、warp 占用率、bank conflict。

### 工具选择（按实际版本查官方文档）

**nsys（Nsight Systems）**：系统级时间线。关键视图：Timeline（排队、空洞、kernel 重叠）、CUDA API（launch 频率与参数）、GPU Utilization。适合找排队、空洞、调度问题、多卡通信。

```bash
nsys profile --trace=cuda,nvtx,osrt --output=report.qdrep python script.py
```

**ncu（Nsight Compute）**：单 kernel 详细分析。关键指标：SM%、Memory Throughput（实际 vs 峰值带宽）、Compute Throughput、Warp Occupancy。适合定位单一 kernel 的计算/内存瓶颈。注意：ncu 开销极大，只 profile 目标 kernel，不用于端到端测量。

```bash
ncu --set full --target-processes all python script.py
```

**引擎自带 profiler**：vLLM `--enable-profiler`（Chrome trace，含调度、prefill/decode、KV cache 事件）；TensorRT-LLM `trtllm-build --profiling`（Layer timing report）。优点：框架语义清晰；缺点：粒度较粗。用法：先用引擎 profiler 找慢的 layer/phase，再用 ncu 深挖具体 kernel。

### 证据解读边界

**可直接读出**：某 kernel 占总执行时间 X%；GPU 整体利用率 Y%；内存带宽达峰值的 Z%。

**可推导**：kernel A 是瓶颈（占比高 + 无优化空间时）；访存受限（带宽饱和 + SM 利用率中等）。

**不能直接断言**：「kernel A 效率低」→ 需与理论峰值或同类 kernel 对比；「GPU 利用率低就是代码问题」→ 可能是 batch size 小、调度慢、输入瓶颈。

**需配合其他证据**：单看 SM 利用率不够，要结合带宽、occupancy、指令 mix；单看某 kernel 慢不够，要看是否在关键路径、占比多少。

### 常见误判

1. **Profiler 自身开销**：开 profiler 后性能下降 2-10 倍。nsys 开销通常 <10%；ncu 重跑 kernel 多次，开销 10 倍+。处理：性能数字用不开 profiler 的测量；profiler 只用于定位；报告时声明「profiling 模式」。
2. **采样不代表稳态**：profiler 抓前 100 个请求包含大量 warmup。处理：warmup 后再开始 profiling，或在 trace 里剔除 warmup 段。
3. **把 kernel 名当证据**：「`kernel_123` 占 50% 时间，它是瓶颈」——不知道这个 kernel 做什么、该有多快。处理：映射 kernel 到算子（Attention/MLP/LayerNorm）；对比实际性能与理论峰值；检查是否因 batch size 小导致效率低。
4. **忽略多卡通信**：单卡 profile 看起来好，多卡吞吐不成比例增长。处理：用 nsys 看多卡 timeline，检查 AllReduce/AllGather 时间与重叠度。

### 正反例

**好的 profiling 报告**：

```text
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

**坏的 profiling 声明**：「profiling 显示 Attention 慢，优化后快了 2 倍」——未说工具与版本、Attention 占比、如何判断「慢」、2 倍提升的基线环境与测量方法。

### 停止规则

- **足够定位**：找到占比 >30% 的热点且知道对应算子/phase。
- **需要深挖**：热点 kernel 内部需要 ncu 看指令级。
- **不需要 profiling**：服务级已明确瓶颈（调度、batch size、资源配置）；GPU 利用率已饱和且吞吐符合预期。

## 与其他文档关系

- [benchmark-protocol](./benchmark-protocol.md)：profiling 只用于定位，绝对性能数字用不开 profiler 的测量
- [perf-topics](./perf-topics.md)：显存、量化、多卡等具体分析
- [anti-patterns](./anti-patterns.md)：profiling 常见误用
