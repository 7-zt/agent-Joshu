# OMP 逐 Skill 触发矩阵

用户自验步骤：确认主包 Skill 在 OMP 中正确加载与触发。**新设备安装第 3 步（omp/setup.md）与新项目安装第 3 步（template/README.md）都以本矩阵收尾。**

## 前提条件

- OMP 已安装（测试版本：18.2.3）
- 已按 [omp/setup.md](../omp/setup.md) 配置 `skills.customDirectories`（指向本仓库 `skills/`）
- 已重启 OMP 使配置生效

## 第 1 步：Skill 被发现

在主包仓库目录开新会话，输入 `/skills` 或查看 Skill 列表，应看到全部 7 个：

inference-ops、grill-me、architect、python-engineering、code-quality、deep-research、unslop

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

## 新项目附加检查（模板安装后执行）

在项目根执行 `git status`，应只见 `agent-joshu/`、`AGENTS.md`、`.gitignore` 与 Trellis 生成物；`.trellis/tasks/`、`.trellis/workspace/` 被忽略（过程本地化生效）。然后在项目目录重跑第 1–3 步。

## 结果记录

| 项目 | 状态 |
| --- | --- |
| 7 个 Skill 列表显示 | ☐ 通过 ☐ 失败 |
| 正向矩阵 1–7 全过 | ☐ 通过 ☐ 失败 |
| 负向检查（2 项） | ☐ 通过 ☐ 失败 |
| 内部链接正常 | ☐ 通过 ☐ 失败 |
| Skill 可独立使用 | ☐ 通过 ☐ 失败 |
| 新项目 git 状态检查 | ☐ 通过 ☐ 失败 ☐ 不适用 |

## 故障排查

1. `skills.customDirectories` 路径是否为设备克隆位置
2. SKILL.md 的 frontmatter 格式是否正确
3. `agents/openai.yaml` 是否存在且格式正确
4. OMP 版本是否支持自定义 Skill 目录

## 注意

- 本验证不需要真实执行 GPU 任务
- 重点验证加载与触发机制，不验证 Skill 功能完整性
- Skill 功能完整性由 [tests/scenarios.md](./scenarios.md) 的场景卡验证
