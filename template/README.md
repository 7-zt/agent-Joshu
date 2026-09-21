# agent-joshu 项目上下文：安装与更新

把主包工作流装进任意项目。安装 3 步；无安装器、无嵌套仓库。

## 新项目安装（3 步）

1. **复制**：把本目录下 `agent-joshu/` 整个复制到目标项目根（与 src、docs、README 同级）。
2. **初始化与并入**：在项目根执行 `trellis init`（生成 `.trellis/` 与 `.omp/`）；把 `agents-rules.md` 全文并入项目根 `AGENTS.md`（放在 Trellis 管理块之外）；把 `gitignore.additions` 的内容追加到项目 `.gitignore`。
3. **验证**：新 OMP 会话跑主包 `tests/omp-loading.md` 触发矩阵；`git status` 应只见 `agent-joshu/`、`AGENTS.md`、`.gitignore` 与 Trellis 生成物——任务过程目录被忽略。

## 更新（手动比对复制）

- 项目内 `agent-joshu/VERSION` 记录本上下文来自的模板版本。
- 主包模板更新后：比对主包 `template/agent-joshu/VERSION` 与项目内版本，手动复制变化的模板文件（`agent-joshu/README.md`、`agent-joshu/adr/README.md`、`agent-joshu/adr/glossary.md`、根级 `agents-rules.md`、`gitignore.additions`）。
- `agent-joshu/adr/` 中的提案与决定是项目自有内容，更新模板时**不得覆盖**；冲突时保留项目版本并在其 ADR「变更」节记录差异。
