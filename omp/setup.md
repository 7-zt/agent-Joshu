# 新设备引导手册

把主包安装到一台新设备，共 3 步。命令均在仓库根目录执行；本手册不含任何设备绝对路径。

## 第 1 步：克隆主包

```bash
git clone <仓库地址> <任意本地目录>
cd <本地目录>
```

## 第 2 步：配置 OMP 加载 Skill

在仓库根目录执行，命令自动取当前路径，勿手工改写为绝对路径：

```bash
# bash
omp config set skills.customDirectories --json "[\"$(pwd)/skills\"]"
```

```powershell
# PowerShell
omp config set skills.customDirectories --json "[\"$($pwd.Path)/skills\"]"
```

- 若该键已有其他目录：先 `omp config get skills.customDirectories --json` 读当前值，合并后再写，不覆盖丢失既有条目。
- 配置键于 OMP 18.2.3 验证、18.2.8 复验；OMP 升级后先 `omp config get <key> --json` 重新确认键名，不猜替代键。
- 写入后重启 OMP 生效。

## 第 3 步：跑触发矩阵验证

新 OMP 会话中按 [tests/omp-loading.md](../tests/omp-loading.md) 的逐 Skill 触发矩阵执行（8 个 Skill 正向 + 2 个负向），全部通过即安装完成。

## memtrace（任务过程记录，主包自带）

- CLI：`memtrace/` Python 包（Python 3.10+，零第三方依赖）。在 bash 中用 `PYTHONPATH=<主包根> python -m memtrace <命令>`，在 PowerShell 中用 `$env:PYTHONPATH=<主包根>; python -m memtrace <命令>` 调用。v1 不提供 pip 安装配置。
- OMP 扩展：`.omp/extensions/memtrace/`——OMP 按项目 `.omp/extensions/` 约定加载（与 Skill 全局加载不同，扩展随项目）。在仓库内开会话即自动生效；`.omp/` 目录整体随主包 git。
- 验证：在仓库根开新 OMP 会话，应出现「memtrace 任务记录已加载」提示（有任务时附当前任务注入）。

## 双模式：全局加载与项目自含

主包支持两种部署模式，可并存（主开发机典型形态）：

- **全局模式（本手册 3 步）**：OMP `skills.customDirectories` 指向本仓库 `skills/`，同设备所有项目共享 8 个 Skill。适合固定主开发机，技能随主包 `git pull` 一处更新。
- **项目自含模式**：目标项目用 `PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>` 把工具包（skills + memtrace CLI + 扩展 + 模板）完整复制进项目（见 [template/README.md](../template/README.md)）。项目 clone 到任意设备（含内网机）即得全部能力，只需该设备装有 OMP + Python 3.10+，无需本仓库。

双模式并存时，项目内 `.omp/skills/`（OMP 自动发现）与全局 customDirectories 同名 Skill 可能双重加载，实际行为以 `tests/omp-loading.md` 双源并存检查的实测记录为准；冲突时回退为任一：统一项目自含（移除全局指向）或依赖全局。

## 工作区规则

- 在本仓库内工作时：根 [AGENTS.md](../AGENTS.md) 自动生效（主包自身维护规则）。
- 在其他项目内工作：bootstrap 安装 `agent-joshu/` 上下文（见上「双模式」与 [template/README.md](../template/README.md)），规则随模板进入项目根 AGENTS.md。

## 可选集成探测

| 集成 | 探测 | 未安装时 |
| --- | --- | --- |
| herdr 多代理 | `test "$HERDR_ENV" = 1` 且 `herdr --help` 可用 | 单代理工作流照常可用 |

任何集成在命令探测失败时：停止并报告，不猜替代命令。
