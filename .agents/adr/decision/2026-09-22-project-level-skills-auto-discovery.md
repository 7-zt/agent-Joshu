# ADR 决定：项目级 .omp/skills/ 自动发现为唯一技能机制

反向决定：2026-09-17-omp-customdirectories-loading.md（设备级 customDirectories 加载方式整体废止；其「仓库文档不写死设备绝对路径」原则由本决定延续）

## 背景

2026-09-22 评审（grill.md 评审记录 4）：「新设备安装主包」路径（clone → 配 customDirectories → 触发矩阵）实践用不了；「安装到设备」概念整体多余。用户模型收敛为：仓库＝纯 git 单位——项目侧 git clone 工具包即用（克隆只是 bootstrap 源，零修改零配置）；主包自我维护也是同一份克隆改代码提交。设备维度没有存在必要。主包与 bootstrap 出去的项目已可完全同构（skills 同在 `.omp/skills/`，OMP 项目级自动发现，S6 运行时实证）。

## 决定

- **唯一机制**：Skill 一律放项目级 `.omp/skills/`，由 OMP 项目级自动发现加载；主包 `skills/` 目录 `git mv` 至 `.omp/skills/`，与 bootstrap 后项目同构。
- **零设备级配置**：不使用、不文档化任何 OMP 全局配置；本机已配置的 `skills.customDirectories` 解除。
- **删除设备维度产物**：omp/setup.md（新设备引导手册）删除；README「新设备安装主包」路径删除；tests 中设备引导场景与双源并存检查删除（单源后无意义）。
- **使用叙事**：新机器零安装——克隆本仓库即用；项目接入用 `memtrace bootstrap`（部署语义见 2026-09-22-project-self-contained-bootstrap.md，不受本决定影响）。

## 真实替代项

- 保留双模式（全局＋项目自含并存）：被否——维护两套机制与文档，且全局模式实践用不了
- skills/ 原位不动、配置不文档化：被否——依赖纸面上不存在的机制，未来的自己无法复现

## 后果

- ✓ 机制单一：主包与项目完全同构，零配置零安装文档
- ✓ 新机器认知负担最低：clone 即用
- ✓ bootstrap 源路径与目标路径同为 `.omp/skills/`，语义更直白
- ✗ skills 进入隐藏目录，仓库浏览时不可见（换取机制单一，接受）
- ✗ 已配 customDirectories 的设备需一次性解除（仅本机一台）

## 重审条件

OMP 上游改变 `.omp/skills/` 项目级自动发现行为时；需要多人共享设备级技能池时。
