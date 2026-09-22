# agent-joshu 项目上下文：安装与更新

把主包工作流装进任意项目。bootstrap 一条命令安装；重跑同一条命令更新。

## 前置

- 设备上有 Python 3.10+（memtrace CLI 的唯一运行时依赖，零第三方库）。
- 主包仓库一份（bootstrap 从中复制；git clone 即用，无需任何设备级配置）。

## 新项目安装（1 条命令）

在主包仓库根执行（目标项目路径替换为实际路径）：

```bash
# bash
PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>
```

```powershell
# PowerShell
$env:PYTHONPATH="."; python -m memtrace bootstrap <目标项目路径>
```

bootstrap 做的事（纯本地复制，零网络）：

1. 复制 `template/agent-joshu/` → 目标 `agent-joshu/`（adr 骨架、VERSION、README）。
2. 复制全部 8 个 Skill → 目标 `.omp/skills/`（不要某技能时加 `--skills <逗号分隔子集>`）。
3. 复制 `memtrace/` 包 → 目标 `agent-joshu/memtrace/`（项目内 CLI：`PYTHONPATH=<项目>/agent-joshu python -m memtrace`）。
4. 复制 `.omp/extensions/memtrace/` → 目标 `.omp/extensions/memtrace/`（OMP 自动加载，优先调用项目内 CLI）。
5. 执行 `memtrace init`（`.agents/memtrace_config.toml` + `.memtrace/`）。
6. 自动追加 `.gitignore`、并入根 `AGENTS.md`（带标记区块；项目已有内容不动）。

`--dry-run` 先预览将执行的动作，不写任何文件。

## 验证

新 OMP 会话跑主包 `tests/omp-loading.md` 触发矩阵；有 git 仓库时 `git status` 应只见 `agent-joshu/`、`.omp/`、`.agents/`、`AGENTS.md` 与 `.gitignore`——`.memtrace/` 任务过程目录被忽略（无 git 项目跳过此判据）；会话开始出现 memtrace 当前任务注入（无任务时安静）。无 git 项目是完全支持的场景（`git_policy` 语义见 `.agents/memtrace_config.toml` 注释；决策见主包 ADR「无 git 项目一等公民支持」）。

## 更新（重跑 bootstrap）

主包模板或组件更新后，重跑同一条命令：

- kit 内容（`.omp/skills/`、`agent-joshu/memtrace/`、`.omp/extensions/memtrace/`、模板静态文件）比对更新，`agent-joshu/VERSION` 与 `bootstrap-manifest.json` 同步。
- 项目自有内容（`agent-joshu/adr/` 中的提案与决定、已并入根 AGENTS.md 的标记区块、`agent-joshu/reports/`）**永不覆盖**，只在漂移报告中列出。
- 你改过的 kit 文件不覆盖：主包新版写入同名 `.new` 文件，由你决定采用与否。
- 主包已删除的内容不清理：漂移报告列出残留，手动删除。
