# 项目结构

## 顶层

```text
agent-Joshu/
├── src/memtrace/             # memtrace 包：任务过程记录 CLI 与 bootstrap 子命令
├── tests/                    # 行为测试、bootstrap 回归、触发矩阵与场景清单
├── .omp/
│   ├── skills/               # 9 个 Skill，OMP 项目级自动发现
│   └── extensions/memtrace/  # OMP 扩展：会话注入当前任务、阶段性提醒
├── template/                 # 项目上下文模板与 bootstrap 静态源
├── .agents/
│   ├── adr/                  # 长期决定（proposal/decision/rejected/archived）
│   ├── rule/                 # 工作规则
│   └── memtrace_config.toml  # 本仓库自身的 memtrace 配置
├── reports/                  # 事实-only 问题报告
├── AGENTS.md                 # 仓库导航与规则加载入口
├── pyproject.toml
├── .pre-commit-config.yaml
├── .gitlint
├── uv.lock
└── Makefile
```

`.memtrace/` 与 `.memtrace-archive/` 是本地任务过程状态，不进 git。

## memtrace 包

`src/memtrace/` 是仓库唯一的 Python 运行时代码：

- `cli.py`：argparse 子命令 `init`、`bootstrap`、`create`、`log`、`read`、`search`、`update`，唯一入口 `python -m memtrace`。
- `store.py`：任务目录扫描、`memtrace.toml` 读写与状态转换（tk schema v1，split 模式）。
- `wal.py`：追加式 WAL 与语义小节（变更、推翻、验证、用户纠正）。
- `config.py`：稀疏 TOML 项目配置。
- `search.py`：历史检索。
- `bootstrap.py`：主包到项目的安装与更新编排。
- `bootstrap_files.py`：文件同步、`bootstrap-manifest.json` 与项目内容合并（AGENTS.md 标记区块、`.gitignore` 幂等追加）。
- `timeutil.py`、`uuid7.py`：时间戳与任务 ID。

新增子命令在 `cli.py` 注册。数据模型改动不碰 schema 字段，并同一次更新 `.omp/skills/memtrace/SKILL.md`；行为回归场景记录在 `tests/scenarios.md`。

## 组件落位

- 新建 Skill 放 `.omp/skills/<name>/`，必须有 `SKILL.md`；目录名与 frontmatter 用英文，正文用中文，自 ruokee-agent-kit 移植的五个 Skill 与 `unslop` 保留英文正文。组件自包含硬规则见 `AGENTS.md`。
- Skill 的附属脚本放该 Skill 自己的 `scripts/`（先例：`summarizer`）。
- OMP 扩展只放 `.omp/extensions/memtrace/`，主包与项目侧共用同一源文件，由 bootstrap 复制分发，不维护第二份。
- 项目侧上下文骨架改 `template/agent-joshu/`；ADR 术语表单源于 `.agents/adr/glossary.md`，由 bootstrap 映射分发，模板不留副本；并入项目根 `AGENTS.md` 的区块源是 `template/agents-rules.md`；`.gitignore` 追加项在 `template/gitignore.additions`。
- 工作规则改 `.agents/rule/`，长期决定走 `.agents/adr/`，问题报告写 `reports/`。

## 依赖边界

- memtrace 只用标准库，兼容 Python 3.10+，路径全用 pathlib，文本统一 UTF-8 与 LF。它会被 vendored 进任意项目，引入一个第三方依赖就破坏安装契约（决定见 [master-kit-ships-code](../adr/decision/2026-09-22-master-kit-ships-code.md)）。
- 语法下限由 `requires-python` 与 ruff `target-version` 固定在 3.10；[code-style-python](./code-style-python.md) 的 3.12+ 与 PEP 695 条目不适用于 `src/memtrace/`，按[规则冲突处理决定](../adr/decision/2026-11-11-rules-bind-agent-io.md)让位于 3.10 契约。
- 工具链（ruff、ty、pytest、pre-commit、gitlint）只进 `pyproject.toml` 的 dev 依赖组，不出现在 bootstrap 产物中。
- OMP 扩展以子进程调用 CLI，不 import Python 代码；CLI 不感知扩展存在。
- `.agents/` 与 `.omp/` 的 Markdown 是手写规则与需同上游逐字节同步的文档，prettier 不重排；`make check-docs` 只检查其余已跟踪 Markdown。

## 部署

部署单元是项目（决定见[project-self-contained-bootstrap](../adr/decision/2026-09-22-project-self-contained-bootstrap.md)）。在主包根执行 `PYTHONPATH=src python -m memtrace bootstrap <目标项目路径>`，按模板、Skills、memtrace、OMP 扩展的顺序复制组件并执行 `memtrace init`；全程零网络，无 git 项目是一等公民场景。安装细节与验证步骤见 [template/README.md](../../template/README.md)。

重跑同一条命令等于更新：项目自有内容（`agent-joshu/adr/`、已并入的标记区块、`agent-joshu/reports/`）永不覆盖；项目改过的 kit 文件写同名 `.new`；主包已删除的内容只列残留不清理。回归验证用 `tests/test_bootstrap.py` 与 `tests/scenarios.md` 场景 9、10。

## 文档与记录

- 长期决定写 `.agents/adr/`，生命周期见其 README。
- 工作规则写 `.agents/rule/`。
- 问题报告写 `reports/YYYY-MM-DD-NN-theme.md`，事实-only。
- 安装与更新指南写 `template/README.md`。
- 任务过程（memtrace 任务、WAL）只留 `.memtrace/` 本地，不进 git。
