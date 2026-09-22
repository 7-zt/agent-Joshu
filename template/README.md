# agent-joshu 项目上下文：安装与更新

把主包工作流装进任意项目。安装 3 步；无安装器、无嵌套仓库。

## 前置

设备上已按主包 `omp/setup.md` 完成 3 步安装（含 memtrace CLI 所需的主包仓库与 Python 3.10+）。

## 新项目安装（3 步）

1. **复制**：把本目录下 `agent-joshu/` 整个复制到目标项目根（与 src、docs、README 同级）；同时把主包 `.omp/extensions/memtrace/` 复制到目标项目 `.omp/extensions/memtrace/`（OMP 自动加载项目本地扩展，负责会话注入与 memtrace-hook 记录）。
2. **初始化与并入**：在项目根执行 `memtrace init`（写 `.agents/memtrace_config.toml`，建 `.memtrace/` 任务根）；把 `agents-rules.md` 全文并入项目根 `AGENTS.md`；把 `gitignore.additions` 的内容追加到项目 `.gitignore`。
3. **验证**：新 OMP 会话跑主包 `tests/omp-loading.md` 触发矩阵；`git status` 应只见 `agent-joshu/`、`AGENTS.md`、`.gitignore`、`.agents/` 与 `.omp/extensions/memtrace/`——`.memtrace/` 任务过程目录被忽略，且会话开始出现 memtrace 当前任务注入（无任务时安静）。

## 更新（手动比对复制）

- 项目内 `agent-joshu/VERSION` 记录本上下文来自的模板版本。
- 主包模板更新后：比对主包 `template/agent-joshu/VERSION` 与项目内版本，手动复制变化的模板文件（`agent-joshu/README.md`、`agent-joshu/adr/README.md`、`agent-joshu/adr/glossary.md`、根级 `agents-rules.md`、`gitignore.additions`）。
- 扩展更新同理：主包 `.omp/extensions/memtrace/` 变化时，向项目内同名目录手动同步。
- `agent-joshu/adr/` 中的提案与决定是项目自有内容，更新模板时**不得覆盖**；冲突时保留项目版本并在其 ADR「变更」节记录差异。
