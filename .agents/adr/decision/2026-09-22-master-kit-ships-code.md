# ADR 决定：主包含代码组件

## 背景

memtrace 落地（见 2026-09-22-memtrace-replaces-trellis.md）需要可执行代码：Python CLI 包与 OMP TypeScript 扩展。此前主包是「纯文档+Skill」仓库；代码放哪是一次长期边界变化。2026-09-22 grill-me 评审 Q10：用户选择主包仓库内新增代码组件，安装契约不变（clone 主包即得全部能力），代价是主包扩展为含代码的仓库。

## 决定

- 主包新增代码组件：`memtrace/`（Python 3.10+ 包，零第三方依赖，标准库实现）与 `.omp/extensions/memtrace/`（TypeScript 扩展）。
- 安装契约不变：git clone 主包即得全部能力；不引入独立仓库、安装器或版本对齐负担。
- 代码纪律：Python 零第三方依赖优先（argparse/pathlib 标准库），Windows 与 Linux 双平台（UTF-8 + LF，pathlib 路径，无平台专属 API）；扩展参考 `.omp/extensions/` 既有形态（ExtensionAPI + node:fs + spawnSync）。
- Skill（`skills/memtrace/`）为代码组件的操作入口，遵守组件自包含硬规则；运行时 owns 任务规则，Skill 只教用法。

## 真实替代项

- 独立仓库（ruokee projects/ 模式变体）——被拒：每台设备多 clone 一个仓库、版本要对齐，「一份克隆装好能力」破例。
- 代码以 pip 包发布后安装——被拒：v1 代码量小，发布管道是纯维护负担。

## 后果

- ✓ clone 即用，Skill/扩展/CLI 同仓库同版本演进
- ✓ Python 零依赖使跨设备安装无 pip 依赖解析风险
- ✗ 主包从纯文档仓库变为含代码仓库，克隆体积与 review 面扩大（v1 代码量小，可控）
- ✗ 代码组件开始承担跨平台回归义务（Windows/Linux 双跑验证）

## 重审条件

代码组件膨胀到需要独立版本节奏或第三方依赖时；出现第二个同等规模代码组件时（重审是否拆仓库）；目标设备 Python 3.10+ 不可用时。
