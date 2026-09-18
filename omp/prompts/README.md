# 可复用 Prompt

本目录存放经真实使用验证的可复用 prompt 模板。**本目录用户可写；Agent 写入前需用户确认。**

## 现有 Prompt

### [design-verify-execute.md](./design-verify-execute.md)

三阶段多代理协作模式：Claude 设计 → Codex 验证 → OMP 执行。

**适用场景**：
- 复杂性能分析任务
- 生产环境部署排障
- 需要独立验证的重要决策

**不适用场景**：
- 简单单步操作
- 只读查询
- 已有明确 SOP 的常规任务

## 继承的验证模式

以下模式继承自参考仓库，已写入对应 Skill 或 AGENTS.md，此处作索引：

### 事实-only 报告消费流程

```text
issue-report 产出事实报告（reports/ 下）→ 新会话/新任务以报告为唯一输入
做 deploy-troubleshoot 排查 → 结论与报告分离存放。
报告本身永不回写分析内容。
```

见：issue-report/SKILL.md

### 版本不明时的一致话术

```text
「该行为依赖 <工具> 的具体版本，当前版本未确认。给出官方文档查询入口 <URL>，
确认版本后我再给确定结论。」——禁止在版本不明时给参数行为断言。
```

见：AGENTS.md 证据纪律

## 使用方式

1. 阅读 prompt 文件的 Goal、输入、证据要求部分
2. 准备 `$ARGUMENTS`（任务描述与上下文）
3. 按 prompt 中的使用方式启动对应代理
4. 保存各阶段产出到任务材料目录

## 新增 Prompt 指南

新增 prompt 前确认：
- 该流程已真实使用 ≥2 次
- 有明确的输入/输出契约
- 有失败条件与边界
- frontmatter 含 description

**不预创建**未经真实使用的 prompt 模板。

## 写入授权

写入本目录需用户确认。确认后：
- 使用 frontmatter 格式
- 包含完整的输入/输出/证据要求/失败条件
- 参考 cleanup-branch.md 的结构密度（来自 ruokee-agent-kit）
