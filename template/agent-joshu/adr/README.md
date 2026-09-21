# 架构决定记录（ADR）

ADR 记录影响长期边界的决定及其理由与契约。不是进度日志、发布说明或临时计划。

## 何时写 ADR

规划需求前先搜索既有提案与现行决定。存在真实替代方案、且选择改变长期边界（架构、所有权、公共契约、持久格式、兼容性、项目级开发与发布策略）时才创建；本地 bug 修复、机械重构、普通文档更新不写 ADR。

## 位置与文档类型

本项目 ADR 根目录为 `agent-joshu/adr`：

```text
agent-joshu/adr/proposal/yyyy-mm-dd-english-slug.md
agent-joshu/adr/decision/yyyy-mm-dd-english-slug.md
agent-joshu/adr/rejected/yyyy-mm-dd-english-slug.md
agent-joshu/adr/archived/yyyy-mm-dd-english-slug.md
```

- 目录同时表达类型与状态，文件内不写 Status 字段；文件名日期为首次提案日期，移动不改。
- 单用户生命周期：提案的批准、拒绝、归档由用户本人当次明确确认；Agent 可起草，不得自行做生命周期决定。

## 提案格式

```markdown
# ADR 提案：<标题>

## 背景
## 提议
## 真实替代项
## 验收标准
## 风险
```

被拒提案移入 `rejected/`，追加 `## 拒绝原因` 后冻结。

## 决定格式

```markdown
# ADR 决定：<标题>

## 背景
## 决定
## 真实替代项
## 后果
## 重审条件
```

- 无冲突更新：文末 `## 变更` 节按日期三级标题追加。
- 反向决定：新建完整决定，新旧头部互链（`反向决定：`/`被反向决定：`），旧决定入 `archived/` 并冻结。

## 作者纪律

「真实替代项」只记真实进入选择的选项；「风险」必须描述可信的危害结果；无可写条目时写「无」，不编造凑数。
