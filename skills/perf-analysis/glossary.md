# 术语表：性能分析

| 术语 | 含义 |
| --- | --- |
| 吞吐（Throughput） | 单位时间产出：tokens/s 或 requests/s。明确统计窗口与是否含 warmup。 |
| TTFT | Time To First Token，首 token 延迟。请求级指标，看分布。 |
| TPOT / ITL | Time Per Output Token / Inter-Token Latency，逐 token 间隔。请求级指标。 |
| P50 / P95 / P99 | 分位数。用于请求级分布；必须随样本量报告。跨运行汇总不用分位数描述。 |
| warmup | 预热请求，不计入统计。冷启动（编译、缓存填充）与稳态需分开测。 |
| 基线（Baseline） | 满足 benchmark-protocol 证据集的初始测量，是对比的锚点。 |
| 混杂因素（Confounder） | A/B 对比中未保持一致的条件，削弱归因效力，必须列出。 |
| KV cache | 键值缓存。显存占用的主要成分之一；命中率影响延迟。 |
| 批处理（Batching） | 请求组批策略：静态批 / 动态批 / continuous batching。 |
| 显存峰值 | 测量窗口内的最大显存占用；OOM 风险的口径。 |
| 质量回归 | 性能改动引起的精度/输出质量变化；适用时与性能同报告。 |
| 未本机复测 | 引用外部数字时的强制标注：该数字来自来源 X 版本 Y，未在目标环境复现。 |
