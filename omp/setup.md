# OMP 落地：安装与版本探测

在 OMP 中启用本工作区的 Skill。以下命令已于 2026-09-17 在本机 OMP 18.2.3 上验证；OMP 升级后配置键可能变化，执行前用 `omp config get <key> --json` 重新确认，不猜替代键。

## 1. 挂载 Skill 目录

OMP 通过 `skills.customDirectories`（数组）加载额外 Skill 目录：

```bash
omp config set skills.customDirectories --json '["C:/Users/admin/Desktop/workspace/workflow/skills"]'
```

- 若该键已有其他目录，先 `omp config get skills.customDirectories --json` 读当前值，合并后再写，不要覆盖丢失既有条目。
- 写入后重启 OMP 会话生效。

## 2. 验证加载

新会话中应能用 `/skill:` 前缀触发四个用户触发型 Skill：

- `/skill:perf-analysis`（推理性能分析）
- `/skill:deploy-troubleshoot`（部署排障）
- `/skill:issue-report`（问题报告）
- `/skill:tech-research`（技术调研）

`inference-stack` 为 Agent 触发型（无 `disable-model-invocation`），按其描述自动匹配。

## 3. 工作区规则

`workflow/AGENTS.md` 是本工作区的 Agent 规则。在该目录（或其子目录）中启动 OMP 会话时会被加载；在其他目录工作时，把需要遵循的规则带上或显式引用该文件路径。

## 4. 可选集成的探测前置

| 集成 | 探测 | 未安装时 |
| --- | --- | --- |
| tk 任务管理 | `command -v tk`（本机 2026-09-17 未安装） | 不使用；不手工伪造 `.tk` 结构；用本目录 `reports/` 与任务材料目录替代 |
| herdr 多代理 | `test "$HERDR_ENV" = 1` 且 `herdr --help` 可用 | 单代理工作流照常可用 |
| 冒烟/隔离测试 | 按需搭建一次性容器环境 | 非必需 |

任何集成在命令探测失败时：停止并报告，不猜替代命令。
