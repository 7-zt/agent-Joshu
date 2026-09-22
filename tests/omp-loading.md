# OMP 逐 Skill 触发矩阵

用户自验步骤：确认主包 Skill 在 OMP 中正确加载与触发。**新设备安装第 3 步（omp/setup.md）与新项目安装第 3 步（template/README.md）都以本矩阵收尾。**

## 前提条件

- OMP 已安装（测试版本：18.2.8）
- 已按 [omp/setup.md](../omp/setup.md) 配置 `skills.customDirectories`（指向本仓库 `skills/`）
- 已重启 OMP 使配置生效

## 第 1 步：Skill 被发现

在主包仓库目录开新会话，输入 `/skills` 或查看 Skill 列表，应看到全部 8 个：

inference-ops、grill-me、architect、python-engineering、code-quality、deep-research、unslop、memtrace

**未显示时**：检查 `skills.customDirectories` 路径（应为设备上克隆位置）；查看 OMP 日志加载错误。

## 第 2 步：正向触发矩阵（每个 Skill 都试一遍）

| # | Skill | 触发方式 | 测试输入 | 预期 |
| --- | --- | --- | --- | --- |
| 1 | inference-ops | 显式 | `/skill:inference-ops` | 进入模式选择/引导 |
| 2 | grill-me | 显式 | `/skill:grill-me` | 进入盘问式需求梳理 |
| 3 | architect | 自动 | 「帮我做这个服务的架构评审和技术选型」 | 自动加载 architect 后作答 |
| 4 | python-engineering | 自动 | 「评估这段 Python 代码的工程实践：<贴代码>」 | 自动加载 python-engineering |
| 5 | code-quality | 自动 | 「这段代码有什么质量问题，该怎么重构？」 | 自动加载 code-quality |
| 6 | deep-research | 自动 | 「深度调研 X，需要来源交叉验证」 | 自动加载 deep-research |
| 7 | unslop | 自动 | 「帮我改写这段报告，去掉 AI 腔」 | 自动加载 unslop |
| 8 | memtrace | 自动 | 「帮我把这个跨会话任务记到 memtrace，先建任务再写第一条阶段记录」 | 自动加载 memtrace，用 create/log 完成 |

**自动触发未生效时**：检查对应 SKILL.md frontmatter 无残留 `disable-model-invocation: true`；`agents/openai.yaml` 的 `allow_implicit_invocation: true`。

## 第 3 步：负向检查（不得隐式触发）

| Skill | 测试输入 | 预期 |
| --- | --- | --- |
| inference-ops | 普通对话提出推理排障话题（不用 `/skill:`） | 不自动进入 inference-ops 流程 |
| grill-me | 「我有个模糊的想法…」（不用 `/skill:grill-me`） | 不自动进入盘问式交互 |

**负向失败时**：检查这两个 Skill 的 `disable-model-invocation: true` 是否仍在。

## 第 4 步：Skill 内部链接与自包含

- Skill 会话中引用内部文档（如 benchmark-protocol）应正确加载，不报文件未找到。
- 将 `skills/inference-ops/` 单独复制到另一位置加入 OMP 配置，应仍能加载使用（组件自包含）。

## 第 5 步：memtrace CLI 与扩展

- CLI：在主包仓库根执行 `PYTHONPATH=. python -m memtrace --version`（bash）应输出 `memtrace 1.0.0`；`python -m memtrace read --list` 在未 init 的目录报「未找到 memtrace 项目」属正常。
- 扩展：主包仓库根开新 OMP 会话，应出现「memtrace 任务记录已加载」提示；`.memtrace/` 存在任务时会话首条注入 `<memtrace-context>` 当前任务与最近 WAL 摘要。

## 新项目附加检查（bootstrap 安装后执行）

在主包仓库根执行 `PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>` 后，逐项核对：

1. **清单核对**：项目内存在 `agent-joshu/`（含 `memtrace/` 包、`VERSION`、`bootstrap-manifest.json`、`adr/` 骨架）、`.omp/skills/` 下 8 个 Skill 目录、`.omp/extensions/memtrace/`（index.ts）、`.agents/memtrace_config.toml`、`.memtrace/`。
2. **git 状态**：项目根 `git status` 只见 `agent-joshu/`、`.omp/`、`.agents/`、`AGENTS.md` 与 `.gitignore`；`.memtrace/` 被忽略（过程本地化生效）。
3. **AGENTS.md 并入**：根 `AGENTS.md` 含 agent-joshu 标记区块（agents-rules.md 全文）。
4. 然后在项目目录重跑第 1–3 步与第 5 步（此时技能来自项目 `.omp/skills/`，memtrace 注入应出现）。

## 双源并存检查（主开发机执行）

前提：OMP 已配 `skills.customDirectories` 指向主包 `skills/`（全局模式），且已 bootstrap 的项目在本机。实测点（S10，行为以实测记录为准）：

1. 在 bootstrap 后的项目根开新 OMP 会话，`/skills` 查看列表。
2. 记录：8 个 Skill 是否正常可见、有无同名重复条目、显式与自动触发是否正常（抽测 1 显式 + 1 自动即可）。
3. 记录：会话开始的 memtrace 注入提示是否出现（此时扩展应优先用项目内 `agent-joshu/memtrace/` CLI——可在项目内 `.memtrace/` 建一条测试任务后重开会话验证注入内容来自本项目）。
4. **若同名冲突或触发异常**：回退任一并记录——统一项目自含（`omp config set` 移除主包指向）或依赖全局；两方向皆可接受，记入结果记录。

## 结果记录

| 项目 | 状态 |
| --- | --- |
| 8 个 Skill 列表显示 | ☐ 通过 ☐ 失败 |
| 正向矩阵 1–8 全过 | ☐ 通过 ☐ 失败 |
| 负向检查（2 项） | ☐ 通过 ☐ 失败 |
| 内部链接正常 | ☐ 通过 ☐ 失败 |
| Skill 可独立使用 | ☐ 通过 ☐ 失败 |
| memtrace CLI 可用 | ☐ 通过 ☐ 失败 |
| memtrace 扩展注入 | ☐ 通过 ☐ 失败 |
| 新项目 git 状态检查 | ☐ 通过 ☐ 失败 ☐ 不适用 |
| 新项目 bootstrap 清单核对（4 项） | ☐ 通过 ☐ 失败 ☐ 不适用 |
| 双源并存检查（含回退记录） | ☐ 通过 ☐ 失败 ☐ 不适用 |

## 故障排查

1. `skills.customDirectories` 路径是否为设备克隆位置
2. SKILL.md 的 frontmatter 格式是否正确
3. `agents/openai.yaml` 是否存在且格式正确
4. OMP 版本是否支持自定义 Skill 目录
5. memtrace 报「未找到项目」：项目根执行 `PYTHONPATH=<主包根> python -m memtrace init`
6. memtrace 扩展无提示：确认 OMP 加载项目 `.omp/extensions/`，且会话 cwd 在含 `.memtrace/` 的项目内

## 注意

- 本验证不需要真实执行 GPU 任务
- 重点验证加载与触发机制，不验证 Skill 功能完整性
- Skill 功能完整性由 [tests/scenarios.md](./scenarios.md) 的场景卡验证
