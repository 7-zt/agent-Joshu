# ADR 决定：移植 ruokee-agent-kit 五个 Skill（英文正文例外 + 自动触发）

## 背景

用户要求把 ruokee-agent-kit（MIT）中除 msgspec 外的五个 Skill（grill-me、python-engineering、architect、code-quality、deep-research）移植到本仓库并支持自动触发。上游正文为英文，约 120 个文件。

## 决定

- 五个 Skill 原样移植（正文不翻译），保留英文，便于与上游 diff 同步；作为中文单语言决定的显式例外。
- 除 inference-ops 维持用户触发外，五个移植 Skill 全部开放模型隐式调用：移除 `disable-model-invocation: true`，`agents/openai.yaml` 设 `allow_implicit_invocation: true`，并为缺失的三个 Skill 补建 openai.yaml。
- 同日调整：应用户要求，grill-me 恢复 `disable-model-invocation: true`（仅用户显式触发），避免模糊请求冷启动进入盘问式交互；其余自动触发不变。
- 同日追加：本地 codex 的 unslop 同规则移植（英文正文、开放隐式调用），上游声明「必须始终应用」，触发信号为撰写/改写任何面向用户的文本。
- 自动触发的路由信号与 Trellis 阶段映射写入 AGENTS.md「Skill 路由（自动触发）」节（Trellis 块外，`trellis update` 不会覆盖）。

## 真实替代项

- 全量翻译为中文（符合单语言决定，但约 120 文件、译后有损且阻断上游同步）
- 保持上游的用户触发设置（不自动触发，违背本次移植目的）
- 修改 `.trellis/workflow.md` 做路由（Trellis 管理的文件，更新时可能被覆盖）

## 后果

- ✓ 对话/Trellis 流程中按信号自动加载，无需 `/skill:` 显式调用
- ✓ 上游更新可直接 diff 合并
- ✗ 工作区存在中英双语言正文，需靠本条目与 AGENTS.md 例外说明约束
- ✗ grill-me 开放隐式调用后，模糊请求可能触发盘问式交互，需用户适应

## 重审条件

上游长期停更或用户阅读障碍明显时，重审是否翻译；自动触发噪声大时，可对个别 Skill 恢复 `disable-model-invocation: true`。
