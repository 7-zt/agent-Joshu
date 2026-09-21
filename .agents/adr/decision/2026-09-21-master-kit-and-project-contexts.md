# ADR 决定：主包与项目侧架构（agent-Joshu 工具包化）

## 背景

2026-09-21 需求评审（grill-me）结论：原工作区与本地信息耦合严重（设备绝对路径、旧仓库路径、仓库外归档引用），换设备无法直接克隆使用；结构层次混乱不利维护；需要跨设备、跨项目复用工作流，并完整保留决策记录用于事后分析。以 ruokee-agent-kit 为结构榜样，但目标是个人可移植，不是公开发布。

## 决定

- **双层架构**：主包（本仓库）＝全局能力层（skills/ + ADR + template/），每台设备 git clone 安装；项目侧＝每个项目根目录一个可见的 `agent-joshu/`（复制 `template/agent-joshu/` + `trellis init`），与 src、docs 同级。
- **记录策略**：决策进 ADR（主包 `.agents/adr/` 与项目 `agent-joshu/adr/` 同构；生命周期 proposal→decision→archived/rejected；单用户由用户当次确认）；任务过程只留本地（.trellis 任务与日志 gitignore + `session_auto_commit=false`）。
- **引导契约**：新设备 ≤3 步（clone → 配 OMP（命令自动取当前路径）→ 逐 Skill 触发矩阵）；新项目 3 步（复制模板 → `trellis init` 并入规则与 gitignore → 触发矩阵 + git 状态检查）。
- **模板更新**：`template/agent-joshu/VERSION` 版本标记 + 手动比对复制；项目自有的 ADR 决定不被覆盖。
- **流程引擎**：保留 Trellis；模板只叠加不改 Trellis 生成物（防 `trellis update` 覆盖）。
- **能力与语言**：六个移植 Skill vendored 原样保留（英文正文例外维持）；中文单语言维持。

## 真实替代项

- Shape B：每项目内 `git clone` 主包作为 `agent-joshu/`（嵌套仓库）——被拒：嵌套 git 仓库内容不会被项目 git 跟踪，决策记录无法随项目仓库走。
- Python 单命令安装器——被拒：git clone 与手动复制已满足需求，避免多余工具与维护面。
- 以 tk 替代 Trellis——被拒：两者使用哲学相近（记录开发过程与复盘），迁移无收益。
- 沿用 DECISIONS.md 平铺单文件——被拒：无法表达生命周期（提案/归档/反向），本决定同日反向了该实践。
- ruokee 式英文主文档 + 中文变体双语——被拒：中文单语言决定维持，公开发布前不引入双倍维护。

## 后果

- ✓ 换设备 git clone + 3 步即用；新项目复制模板即得同构上下文
- ✓ 决策记录完整随 git 走、可跨项目分析；过程状态不再污染版本库
- ✓ 仓库自包含、零设备路径耦合（check-workflow.ps1 第 7 节断言）
- ✗ 多设备同时写决策文件可能 git 冲突（低频，手动处理）
- ✗ 模板更新靠手动比对复制（版本标记提示漂移）
- ✗ `trellis update` 理论上可覆盖 .omp 生成物（对策：模板只叠加）

## 重审条件

需要多人协作或公开发布时（重审语言与分发方式）；Trellis 停更或严重不匹配需求时（重审流程引擎）；模板手动更新成为实际负担时（重审自动更新工具）。
