# 代码管理

## 分支

每个任务使用独立分支，分支名使用任务类型前缀：

- `feature/<slug>`
- `fix/<slug>`
- `docs/<slug>`
- `refactor/<slug>`

禁止使用 `codex/`、`claude/`、`agent/` 等工具名作为前缀。禁止直接在 `main` 上修改。

本仓库禁止使用 Git worktree。

## 提交

一个提交只包含当前任务的一个原子变更。不要提交未识别的脏文件，不要用提交夹带无关格式化或重构。

提交信息使用 Conventional Commits：

```text
<type>(scope)!?: topic

- body line
- body line
```

- `type` 使用小写 ASCII 字母，常用 `feat`、`fix`、`docs`、`refactor`、`perf`、`test`、`build`、`chore`。
- `scope` 必填，只能是 `agents`、`api`、`build`、`config`、`core`、`docs`、`lib`、`repo`、`test` 之一。
- `topic` 非空，建议使用中文。
- body 必须存在，必须是顶格无序列表，不允许缩进、空行和非列表行。
- footer 可选，与 body 之间空一行，使用 Git trailer 风格。
- GitLab MR 合并生成的 squash 提交例外：消息为标题、空行、`Refs: <project>!N`，没有 body。

`amend` 只允许修改提交信息，不允许补充或替换已提交的文件。需要修正内容时新增提交，最终用 squash merge 收敛。

## 检查

开发完成后的第一动作是 `git commit`，让 pre-commit 和 commit-msg hooks 执行完整检查。不要先用 `make check` 或零散检查替代 hooks。

hook 报具体错误时，才运行 `make check USE_COLORS=0` 或更小范围命令定位。hook 自动修复 `end-of-file-fixer`、`trailing-whitespace`、`ruff check --fix`、`ruff format` 后，确认变更属于当前任务，重新 `git add` 和 `git commit`。

依赖变更使用 `uv add`、`uv remove` 和 `uv lock`。禁止手工编辑 `uv.lock`。

## 合并

任务分支合并到 `main` 使用 squash merge，合并后删除任务分支，本地和远端都删除。即使可以 fast-forward，也不改用普通 merge 或 rebase。

通过 GitLab MR 合并时使用项目 squash 提交模板，消息为标题加 `Refs: <project>!N`，不拼接 MR description。没有 MR 的本地合并按提交规则写列表 body。

合并前必须取得用户对分支内容的审查确认和明确授权。用户说「提交」默认指提交到任务分支，不代表授权合并或推送。

`main` 保持线性。

tag 只允许打在 `main` 上。

## 任务材料

任务编号、计划、验证记录和临时脚本不进入代码库。长期材料放在任务目录，临时文件放在 `tmp/`，`tmp/` 不作为正式提交内容。
