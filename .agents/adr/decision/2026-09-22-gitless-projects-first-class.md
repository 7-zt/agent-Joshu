# ADR 决定：无 git 项目一等公民支持

## 背景

2026-09-22 评审（grill-no-git.md，触发场景 optuna4h20：目录树 6 层内无任何 .git）核实：agent-joshu 装入无 git 项目后三处契约落空——扩展会话快照静默失效（`git status` 失败直接 return，不留痕迹）；`git_policy` 是校验通过但零行为的死键，而 bootstrap 无条件追加 `.memtrace/` 忽略规则与 `track` 语义直接冲突；`agents-rules.md`/`memtrace/SKILL.md` 的「进 git」措辞指向不存在的动作。用户选姿态 A（显式支持、最小改动），本次决定即授权。主包安装方式本身是复制文件夹（bootstrap），撞上无 git 环境（临时项目、内网整包复制）概率不低，声明 git 为隐含前置（姿态 B）会关掉这类项目。

## 决定

- **无 git 是显式已知状态，不是错误状态**：全部组件在无 git 项目中保持可用；受影响的仅是「与 git 交互」的边缘能力，以显式降级呈现。
- **扩展 hook 显式降级**：会话开始 `git status` 失败且存在非 closed 任务时，写一条 actor=`memtrace-hook` 的「快照不可用（无 git 仓库）」WAL 条目（含 session 与退出码）；无任务时保持安静；git 仓库干净工作区行为不变。
- **`git_policy` 获得真实语义**：`ignore`（默认）＝ bootstrap 幂等追加 `.memtrace/` 等忽略规则；`track` ＝ 任务过程进项目 git，bootstrap 跳过追加，检测到既有忽略块时在漂移报告提示冲突；`none` ＝ 不管理，bootstrap 不碰 `.gitignore`。`memtrace init` 提示语按有效值条件化。
- **文档措辞条件句**：「进 git」类表述（agents-rules.md、memtrace/SKILL.md）与 `git status` 验收判据（README、template/README、omp-loading、scenarios）一律加「有 git 仓库时」前提；无 git 项目跳过对应检查项。
- **范围声明（红线）**：不实现 `git_policy=track` 的自动 add/commit；不用内容哈希＋文件清单模拟版本历史。

## 真实替代项

- 声明 git 为隐含前置（姿态 B：只改 README 写明假定）——被拒：关掉临时项目与内网复制项目这类合法场景，且死键与静默降级照旧误导。
- 维持现状（姿态 C：只记录事实）——被拒：排障时对 `git_policy` 作用的误判最费时间；静默缺失让 WAL 历史出现无法解释的空洞。
- `git_policy=track` 自动提交——被拒：无真实痛点前造机制（grill-no-git Q3 补充声明，用户认可）。
- 哈希清单模拟版本历史——被拒：同上；版本历史是 git 的职责，不是 memtrace 的。

## 后果

- ✓ 无 git 项目（临时、内网复制）从「未决状态」变为「已决的显式降级」；三个月后翻 WAL 可判断某段时间为什么没有变更清单
- ✓ `git_policy` 三值有真实行为，消除死键误判
- ✗ 无 git 项目会话首条 WAL 多一条快照不可用条目（仅存在 open 任务时；接受，可见性优先于安静）
- ✗ `track` 与既有忽略块的冲突靠人工消除（bootstrap 只报告不删改 .gitignore；授权边界使然）
- ✗ 无 git 项目继续没有回滚与归因的 git 能力（属项目侧取舍，见 grill-no-git 第 12 节档位 b；不在主包职责内）

## 重审条件

项目侧出现「无 git 造成实际损失」（grill-no-git 第 12 节档位重审触发）时重审该项目的 git 引入；OMP 上游提供仓库状态 API 可替代 spawnSync 探测时重审实现载体；`track` 出现真实自动提交需求时重审范围红线。
