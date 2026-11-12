# ADR 决定：引入 uv + pre-commit + gitlint + make 开发检查链

## 背景

PR #3 评审指出删除检查类规则后仓库缺少提交前检查，要求把 servio-sglang 的检查相关规则原文加回，并落地对应工具链让规则可执行。此前这些条目按 `2026-11-11-rules-bind-agent-io` 的冲突条款处理：设施不存在即不适用。用户在同日明确选择「照搬规则 + 落地工具链」。

## 决定

- 检查相关规则（`code-management.md`、`testing.md`、`document-writing.md` 的「检查」节）按 servio-sglang 原文恢复，措辞不改。
- 落地工具链：`pyproject.toml` 的 dev dependency-group（gitlint-core、pre-commit、pre-commit-hooks、pytest、ruff、ty）与 `uv.lock`；`.gitlint` 与 `.pre-commit-config.yaml` 驱动 commit-msg 与 pre-commit 钩子；`Makefile` 提供 `check`、`check-docs` 等目标。
- 与 servio 的三处差异：不引入 flake8 project-linter（servio 私有插件，随其源码维护）；prettier 不带 servio 私有插件（compact-markdown-table、zhfmt）；prettier 排除 `.agents/` 与 `.omp/`（手写规则文档与需同上游保持逐字节同步的 Skill 文档不做机器重排）。
- memtrace 运行时零第三方依赖契约不变：工具链只存在于开发依赖组，bootstrap 装出的项目不携带任何依赖，`2026-09-22-master-kit-ships-code` 的安装契约不受影响。

## 真实替代项

- 适配移植，命令改用系统 `python` 直接执行。被拒：用户要求与 servio 同构的机器强制检查，两仓库心智模型一致。
- 原样照搬规则、不落地工具链。被拒：规则再次成为死文本，回到 PR #3 删除前的状态。

## 后果

- ✓ 提交信息与代码检查由钩子机器强制，模型与人都无法绕过
- ✓ 检查规则与 servio 逐字一致
- ✗ 克隆后需要 `make sync` 与 `make install-pre-commit` 两步初始化，「git clone 即用」弱化为「clone + 两命令可用」
- ✗ Windows 无 make 时 `make check` 与 `make check-docs` 不可用，需直接运行等价命令（`uv run --no-sync pre-commit run --all-files` 等）

## 重审条件

钩子链在 Windows 上的体验持续劣化（路径、性能、换行符问题）时；memtrace 引入运行时依赖、pyproject 需要承载打包元数据时；servio 检查链大幅演进需要重新对齐时。

## 变更

### 2026-11-12

《文档撰写》「检查」节的排除范围由 `servio/` 改为本仓库实际行为（`.agents/` 与 `.omp/`），消除照搬原文时的 servio 残留；该节其余措辞不变。
