---
name: deploy-troubleshoot
description: 用于部署问题分层排查的证据优先工作流：环境/驱动/依赖/服务逐层收敛，复现条件记录，最小化复现，事实与假设分离。
disable-model-invocation: true
---

# 部署排障（Deploy Troubleshoot）

用于大模型推理系统部署问题的诊断与排查：环境配置、驱动兼容、依赖冲突、容器编排、服务启动、版本兼容、资源与权限。方法：分层排查、逐层收敛、假设显式验证。

## 适用范围

覆盖四类工作：问题定界、分层排查、复现确认、workaround 验证。

边界之外：代码逻辑 bug、产品功能设计、性能优化（非资源不足类），遵循各自常规流程。本 Skill 不做自动修复；解决方案经用户确认后执行。

## 模式选择

| 模式 | 触发 | 阅读 |
| --- | --- | --- |
| 快速排查 | 默认：单一明确错误、已有报错信息 | `./workflow/quick-troubleshoot.md` |
| 系统排查 | 用户显式要求「系统排查」「完整诊断」「从头排查」，或快速排查未定位 | `./workflow/full-troubleshoot.md` |

## 判断顺序

1. 收集初始证据：错误信息全文（含时间戳与上下文）、日志片段、失败现象。
2. 定界层次：硬件 → 驱动 → 系统 → 容器/运行时 → 依赖 → 服务 → 应用，按信号强度选自顶向下或自底向上。
3. 每层：提出假设 → 设计验证 → 记录结果 → 收敛或下探。
4. 收敛到根因（已验证）或给出带风险的 workaround（明示临时性）。

| 信号 | 阅读 | 常配对 |
| --- | --- | --- |
| 分层排查方法、自底向上/自顶向下 | [layered-diagnosis](./references/layered-diagnosis.md) | evidence-collection, reproduction-and-bisect |
| 最小化复现、变更历史二分、复现率统计 | [reproduction-and-bisect](./references/reproduction-and-bisect.md) | layered-diagnosis, resolution-rollback-and-closure |
| 命令五元组、日志提取、配置导出、脱敏 | [evidence-collection](./references/evidence-collection.md) | environment-snapshot, layered-diagnosis |
| Python虚拟环境、包冲突、运行时库、ABI兼容 | [dependency-and-runtime-boundaries](./references/dependency-and-runtime-boundaries.md) | layered-diagnosis, container-network-permission |
| 容器诊断、网络路径、文件权限、SELinux | [container-network-permission](./references/container-network-permission.md) | layered-diagnosis, dependency-and-runtime-boundaries |
| OOM、显存不足、磁盘满、文件描述符耗尽 | [resource-exhaustion](./references/resource-exhaustion.md) | layered-diagnosis |
| 方案分级、回退准备、验证标准、问题闭环 | [resolution-rollback-and-closure](./references/resolution-rollback-and-closure.md) | reproduction-and-bisect, layered-diagnosis |
| 常见错误做法与识别模式 | [anti-patterns](./references/anti-patterns.md) | 所有其他 references |
| 采集环境快照、记录验证命令、脱敏规则 | [environment-snapshot](./references/environment-snapshot.md) | evidence-collection |
| 术语含义不清或不一致 | [术语表](./glossary.md) | — |

领域知识（各引擎具体报错含义、版本兼容表）不在本 Skill 内维护。需要时从官方文档采集证据：① 明确来源 URL 与版本；② 访问日期；③ 完整错误信息与上下文；④ 版本不明时声明「需确认当前版本」。

## 证据要求

- 环境事实必须来自实际命令输出（`nvidia-smi`、`python --version`、`pip show`、镜像 digest 等），记录命令文本、退出码、输出摘要；不得凭记忆或猜测填写版本。
- 错误信息给完整关键片段（含时间戳、上下文行），不做截断式转述。
- 每个假设必须可验证：给出验证命令或操作步骤；未验证的假设不得作为结论。
- 涉及具体工具版本的行为：版本不明时写「需确认当前版本」，不基于某版本假设下结论。
- 输出区分：观测事实（observed）、假设（hypothesis）、验证结果（verified/refuted）、临时方案（workaround）、根因（root cause，须已验证）、用户决策。

## 授权边界（命令分级）

| 级别 | 例 | 规则 |
| --- | --- | --- |
| L0 只读 | `nvidia-smi`、日志读取、`pip show`、配置查看 | 可直接执行 |
| L1 本地可逆 | 建临时目录、复制文件、运行诊断脚本 | 说明意图后执行 |
| L2 改变环境 | 安装/卸载依赖、改配置、重建容器、清理缓存 | 给出命令文本与预期影响，用户确认后执行 |
| L3 影响运行系统 | 重启服务、终止进程、生产变更 | 必须用户明确授权 + 给回退方法 |

用户请求「排查」不自动授权 L2/L3。报告写入授权与环境修改授权是两件事。

## 输出契约

- 给问题定界、候选根因（多个时全列出，按证据强度排序）、每个根因的验证步骤、解决方案候选。
- 方案包含：操作步骤、预期结果、回退方法、风险提示；区分临时 workaround 与根本解决。
- 排查记录保留：复现条件、已排除项、验证结果、待确认项。

## 停止规则

- 证据不足不断言根因；不把「可能是」写成「确定是」。
- 不把相似报错当同一问题，需验证共享根因。
- 不自动执行 L2/L3 命令。
- 不跳层直猜应用层问题（除非有明确信号）。
- 只读模式不修改环境；写入排查报告的既有授权仍然适用。
