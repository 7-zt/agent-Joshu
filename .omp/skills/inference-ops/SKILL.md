---
name: inference-ops
description: 大模型推理系统部署排障与性能优化的证据优先工作流：分层排查、复现与二分、基线测量、瓶颈定位、事实-only 问题报告、技术调研与知识沉淀。性能数字必须附完整证据集；版本不明不给行为断言。
disable-model-invocation: true
---

# 推理运维（Inference Ops）

大模型推理系统的部署排障与性能优化：环境配置、驱动兼容、依赖冲突、容器编排、服务启动、资源与权限；吞吐、延迟、显存、资源利用率、并发能力、长序列处理。方法：分层定位、假设显式验证、证据优先。模型负责主要推理；参考文档提供方法论与证据规范，不替代项目事实。

## 适用范围

覆盖六类工作：问题定界与分层排查、复现确认、workaround 验证；基线测量、瓶颈定位、参数调优与改动对比；事实-only 问题报告；技术调研与知识条目沉淀。

边界之外：代码逻辑 bug、产品功能定义、业务优先级判断，遵循各自常规流程。本 Skill 不做具体代码实现与自动修复；解决方案经用户确认后执行。项目事实来自当前代码与配置；优先级属于用户。

## 模式选择

| 模式 | 触发 | 阅读 |
| --- | --- | --- |
| 快速 | 默认：单一明确错误，或单一性能问题、小 diff 自检 | `./workflow/quick.md` |
| 完整 | 用户显式要求「系统排查」「完整诊断」「完整分析」「全面 profiling」，或快速模式未定位 | `./workflow/full.md` |
| 咨询与调研 | 方案讨论、工具对比、调优思路；或结构化技术调研与学习报告 | `./workflow/consult.md` |
| 问题报告 | 用户要求「记录问题」「写问题报告」 | `./references/reporting.md` |

## 判断顺序

- **排障类**：收集初始证据（错误信息全文含时间戳与上下文、日志片段、失败现象）→ 定界层次（硬件 → 驱动 → 系统 → 容器/运行时 → 依赖 → 服务 → 应用，按信号强度选自顶向下或自底向上）→ 每层：提出假设 → 设计验证 → 记录结果 → 收敛或下探 → 根因（已验证）或带风险的 workaround（明示临时性）。
- **性能类**：识别主要关注点（吞吐、延迟、显存、利用率，还是成本）→ 判定所处阶段（无基线 / 有基线未定位 / 已定位待验证 / 已验证待对比）→ 按信号阅读参考文档，只读当前需要的 → 只报告有充分证据的结论；证据不足时输出「待验证假设」与建议采集命令。

## 参考文档导航

| 信号 | 阅读 | 常配对 |
| --- | --- | --- |
| 设定性能目标、约束与权衡框架 | [analysis-thinking](./references/analysis-thinking.md) | benchmark-protocol, bottleneck-localization |
| 设计 benchmark、统计口径、测量误差、显著性判断 | [benchmark-protocol](./references/benchmark-protocol.md) | anti-patterns, bottleneck-localization |
| 分层定位瓶颈、读取 profiler 数据、区分计算/内存/通信 | [bottleneck-localization](./references/bottleneck-localization.md) | perf-topics, benchmark-protocol |
| 吞吐延迟权衡、显存与 KV cache、量化评估、多卡并行 | [perf-topics](./references/perf-topics.md) | bottleneck-localization, analysis-thinking |
| 分层排查方法、复现与二分、解决回退与收尾 | [layered-diagnosis](./references/layered-diagnosis.md) | deploy-common-causes, evidence-and-snapshot |
| 依赖冲突、运行时边界、容器/网络/权限、资源耗尽 | [deploy-common-causes](./references/deploy-common-causes.md) | layered-diagnosis |
| 命令五元组、日志提取、环境快照、脱敏 | [evidence-and-snapshot](./references/evidence-and-snapshot.md) | 所有排障与测量场景 |
| 事实-only 问题报告模板、调研报告骨架、来源分级、论断分类 | [reporting](./references/reporting.md) | 所有输出场景 |
| 常见错误做法与识别模式 | [anti-patterns](./references/anti-patterns.md) | 所有其他 references |
| 知识条目建库协议、审计元数据、条目模板 | [knowledge-base](./references/knowledge-base.md) | reporting |
| 术语含义不清或不一致 | [术语表](./glossary.md) | — |

领域知识（引擎机制、参数行为、版本兼容）不在本 Skill 内凭记忆生成。需要时先查知识库（见 [knowledge-base](./references/knowledge-base.md)），未入库则从官方文档采集证据：① 明确来源 URL 与版本；② 访问日期；③ 标注论断类型（事实/推断/判断/宣传/未解决）；④ 版本不明时声明「需确认当前版本」。

## 证据要求

- **环境事实来自实际命令输出**（`nvidia-smi`、`python --version`、`pip show`、镜像 digest 等），按命令五元组记录（见 evidence-and-snapshot）；不得凭记忆或猜测填写版本。
- **数字类断言的最低证据集**：① 测量环境（硬件、驱动、CUDA/框架/引擎及版本）；② 完整可复现命令；③ 负载定义（模型与精度、输入/输出 token 分布、并发或到达模型、请求数或时长、warmup、缓存状态、客户端与服务端位置）；④ 统计口径（请求级分布与跨运行统计分开，见 benchmark-protocol）；⑤ 样本数。缺任一项，该数字只能以「未完成测量」标注呈现。
- 加速倍数/提升百分比必须同时给出基线与改后的完整证据集和可复现步骤；单次运行、「理论上」、官方宣传数字（未在本机复测）都不构成有效证据，引用外部数字必须标注来源与版本并声明「未本机复测」。
- 错误信息给完整关键片段（含时间戳、上下文行），不做截断式转述。
- 每个假设必须可验证：给出验证命令或操作步骤；未验证的假设不得作为结论。
- 推导结论（容量估算、延迟预测、成本推算）展示输入、公式、不确定性。
- 涉及具体引擎参数行为：版本不明时写「需确认当前使用版本」，不给确定的行为断言。
- 输出至少区分：观测事实（带 `path:line`、配置键、命令输出）、推导、未验证假设、验证结果（verified/refuted）、临时方案（workaround）、根因（root cause，须已反向验证）、建议、用户决策。

## 授权边界（命令分级）

| 级别 | 例 | 规则 |
| --- | --- | --- |
| L0 只读 | `nvidia-smi`、日志读取、`pip show`、配置查看 | 可直接执行 |
| L1 本地可逆 | 建临时目录、复制文件、运行诊断脚本 | 说明意图后执行 |
| L2 改变环境 | 安装/卸载依赖、改配置、重建容器、清理缓存、benchmark 与 profiling 等产生负载的命令 | 给出命令文本与预期影响，用户确认后执行 |
| L3 影响运行系统 | 重启服务、终止进程、生产变更 | 必须用户明确授权 + 给回退方法 |

用户请求「排查」「分析」不自动授权 L2/L3。报告写入授权与环境修改授权是两件事，分别确认。

## 输出契约

- 排障：给问题定界、候选根因（多个时全列出，按证据强度排序）、每个根因的验证步骤、解决方案候选（操作步骤、预期结果、回退方法、风险提示；区分临时 workaround 与根本解决）。
- 性能：给候选方案及各自的权衡与适用条件，不给单一答案；陈述每个判断依赖的假设。改进建议必须包含：预期收益区间（含不确定性）、实现成本、验证方法、回退方案。
- 技术取舍转译为成本/风险/时间；优先级由用户设定。
- 排查与分析记录保留：复现条件、已排除项、验证结果、待确认项。

## 知识沉淀

值得复用的引擎知识按 [knowledge-base](./references/knowledge-base.md) 协议入库：条目带 source/version/accessed/last_reviewed/status 审计元数据，一场景一条目，不预生成空壳。`needs-review`/`expired` 条目不得当作确定事实引用。

## 停止规则

- 证据不足不断言根因或瓶颈；不把「可能是」写成「确定是」；根因未反向验证时写「最可能原因（已排除 A/B，未排除 C）」。
- 无基线时不推荐优化参数、不断言「XX 慢」；只输出待验证假设与采集计划。
- 不把相似报错/性能现象当同一问题，需验证共享根因；不跳层直猜应用层问题（除非有明确信号）。
- 不在混合多个变量后归因单一因素；A/B 对比只改一个目标变量，混杂因素必列。
- 不把理论加速比当实测结果；不推荐未在目标环境验证的参数。
- 不为满足方法论编造发现；没有瓶颈/问题时零发现是有效结果；「未定位 + 下一步计划」是合法结论。
- 不自动执行 L2/L3 命令；只读与咨询任务不修改被审查文件与环境；写入报告的既有授权仍然适用。
- 不报告 profiler 能机械生成的原始 trace；提炼关键瓶颈与方向。
