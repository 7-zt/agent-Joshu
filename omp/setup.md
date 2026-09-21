# OMP 落地：安装与版本探测

在 OMP 中启用本工作区的 Skill。以下命令已于 2026-09-17 在本机 OMP 18.2.3 上验证；OMP 升级后配置键可能变化，执行前用 `omp config get <key> --json` 重新确认，不猜替代键。

## 1. 挂载 Skill 目录

OMP 通过 `skills.customDirectories`（数组）加载额外 Skill 目录：

```bash
omp config set skills.customDirectories --json '["C:/Users/admin/Desktop/yuting/program/agent-Joshu/skills"]'
```

- 本仓库 2026-09-21 自 `C:/Users/admin/Desktop/workspace/workflow` 迁移而来；若配置仍指旧路径，按上面命令更新。

- 若该键已有其他目录，先 `omp config get skills.customDirectories --json` 读当前值，合并后再写，不要覆盖丢失既有条目。
- 写入后重启 OMP 会话生效。

## 2. 验证加载

新会话中应能用 `/skill:inference-ops`（推理运维：部署排障 + 性能优化）触发，也应看到 2026-09-21 移植的六个 Skill：grill-me、architect、python-engineering、code-quality、deep-research（源自 ruokee-agent-kit）与 unslop（源自本地 codex，触发信号：撰写/改写面向用户的文本）。均可 `/skill:<name>` 显式触发；除 grill-me 与 inference-ops 仅用户显式触发外，其余五个允许模型隐式调用，对话匹配触发信号时自动加载（见 AGENTS.md「Skill 路由（自动触发）」）。

## 3. 工作区规则

`AGENTS.md`（仓库根）是本工作区的 Agent 规则。在本仓库（或其子目录）中启动 OMP 会话时会被加载；在其他目录工作时，把需要遵循的规则带上或显式引用该文件路径。

## 4. 可选集成的探测前置

| 集成 | 探测 | 未安装时 |
| --- | --- | --- |
| tk 任务管理 | `command -v tk`（本机 2026-09-17 未安装） | 不使用；不手工伪造 `.tk` 结构；用本目录 `reports/` 与任务材料目录替代 |
| herdr 多代理 | `test "$HERDR_ENV" = 1` 且 `herdr --help` 可用 | 单代理工作流照常可用 |
| 冒烟/隔离测试 | 按需搭建一次性容器环境 | 非必需 |

任何集成在命令探测失败时：停止并报告，不猜替代命令。
