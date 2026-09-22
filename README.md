# agent-Joshu：个人 AI 工作流主包

## 前言

你在使用 Agent 时，是否遇到过这些情况？

- 大模型给出的结果和你的目标总是存在差距，反复补充要求后仍达不到预期。
- 任务一旦缺少持续交互，随着上下文变长，Agent 会逐渐偏离目标，而你很晚才发现。
- 为了纠正大模型幻觉，只能重新复制一大段材料并开启新会话，但新会话会丢失旧会话里的隐含信息、取舍过程和失败经验。
- Token 花得越来越多，任务却没有更稳定地朝预想方向推进。

这些问题不全是模型能力问题。很多时候，真正缺少的是一套稳定的使用方法：哪些上下文需要长期保存，事实和推断如何区分，什么时候必须停下来验证，任务跑偏后怎样恢复，以及一次任务里的经验如何进入下一次任务。

我在入职后真实的线上开发中逐渐意识到，人与人之间的经验差距只能靠时间积累，但具体的动手能力越来越体现在如何使用 Agent。回头看，我原来的方法其实很原始，主要是和 Agent 直接对话，再加上一些简单的工具调用。上下文、验证、授权、任务记录和经验复用都没有形成固定方法，模型的能力也没有被稳定地发挥出来。

因此，我以 [ruokee-agent-kit](https://github.com/ruokee/ruokee-agent-kit) 的结构和能力模式为起点，结合自己在模型部署、推理优化、框架与算子优化方向的使用经验，补充了 `inference-ops`、项目模板、ADR、证据规范和回归检查等，形成了这套更适合个人长期使用的 Agent 工作包。

它主要解决以下问题：

- 把长期规则、项目决策和临时任务过程分开保存，减少上下文污染，也降低切换会话时的信息损失。
- 按任务类型加载对应 Skill，不让所有规则一次性塞进上下文。
- 要求重要结论附带代码、配置、命令输出、版本或来源，避免把猜测写成事实。
- 用固定模板把同一套工作方式带到不同设备和项目，不依赖某台机器上的绝对路径。
- 在条件允许时，把方案设计、独立验证和实际执行拆开，尽早发现 Agent 已经跑偏。

这套工具并不追求让 Agent 完全无人看管，也不打算用一堆规则替代工程判断。它更像一个个人工作台，让 Agent 在长任务、跨会话和多项目环境里保持方向，并让每一次失败、修正和决定都有地方可查。

现在我把它分享出来，希望能帮到和我曾经一样，只会不断补提示词、重开会话，却仍然无法稳定获得理想结果的人。

### 适用人群

- 经常使用 Codex、Claude Code、OMP 等编码 Agent，并开始处理长任务或跨会话任务的开发者。
- 从事大模型部署、推理优化、框架或算子优化，希望把排障和性能分析过程固定下来的人。
- 想建立个人 Agent 工作流，又不希望一开始就搭建复杂平台的个人开发者和小团队。
- 在意事实依据、版本差异、操作授权和结果可复现性的人。

### 适用范围

- 需求梳理、技术调研、架构设计、Python 工程实践、代码质量评审和文档改写。
- 大模型推理服务的部署排障、性能分析、基线测量、问题报告和知识沉淀。
- 项目上下文管理、架构决定记录、跨设备安装和新项目初始化。
- 单 Agent 工作流，以及 Herdr 可用时的多 Agent 设计、验证和执行分工。

涉及依赖安装、环境修改、容器重建、服务重启或生产变更时，本项目只提供分级和检查方法，实际操作仍需要明确授权。

推理优化 × 部署排障方向的个人 Agent Kit。**主包一份克隆，项目一条命令。** 核心理念：证据优先、事实与推断分离、版本敏感断言必须可审计、跨设备零路径耦合。

## 架构

- **主包（本仓库）**：复杂源仓——Skill 库 + 跨项目决策与经验（ADR）+ 项目上下文模板（`template/`）+ 代码组件（`memtrace/` CLI、`memtrace bootstrap` 子命令、OMP 扩展）。主开发机可按 `omp/setup.md` 配置全局加载（双模式见该文档）。
- **项目侧（自含）**：主包根一条命令 `PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>` 装入完整工具包——可见的 `agent-joshu/`（模板 + adr + vendored `memtrace/` CLI + VERSION + manifest）+ `.omp/skills/`（8 个 Skill，OMP 自动发现）+ `.omp/extensions/memtrace/`。项目 clone 到任意设备（含内网机）即得全部能力，只需该设备装有 OMP + Python 3.10+；重跑同命令＝比对更新，项目自有内容永不覆盖。
- 记录策略：决策随项目 git 走（`agent-joshu/adr/`）；任务过程留本地（`.memtrace/`）。

```text
主包（源仓，主开发机）              每个项目（自含，任意设备含内网机）
├── skills/（8 个）    ──复制─►     .omp/skills/（OMP 自动发现）
├── memtrace/ + 扩展   ──复制─►     agent-joshu/memtrace/ + .omp/extensions/
├── template/agent-joshu/ ──►       agent-joshu/（adr 骨架 + VERSION + manifest）
└── .agents/adr/（跨项目决策）      AGENTS.md / .gitignore（标记区块并入）
                                    .memtrace/（任务过程，本地 gitignore）
```

## 目录

```
├── README.md            本文件
├── LICENSE              本项目 MIT License
├── THIRD_PARTY_NOTICES.md 第三方来源与许可声明
├── AGENTS.md            主包工作区规则（架构、Skill 路由、证据纪律、授权分级、存储约定）
├── .agents/adr/         架构决定记录（proposal/decision/archived/rejected 生命周期 + 术语表）
├── skills/              Skill 库（OMP 全局加载，见 omp/setup.md；6 个移植 vendored + inference-ops + memtrace 原创）
├── memtrace/            memtrace Python 包（任务过程记录 CLI + bootstrap 部署子命令，零第三方依赖）
├── template/            项目上下文模板（agent-joshu/ 目录源 + agents-rules.md + 安装说明 + 版本标记）
├── reports/             主包自托管工作的问题报告（YYYY-MM-DD-NN-theme.md，事实-only）
├── omp/                 setup.md（新设备 3 步引导）、prompts/（可复用模式索引 + 独立 prompt）
├── tests/               逐 Skill 触发矩阵（omp-loading.md）与场景回归卡（scenarios.md）
├── .memtrace/           任务过程（memtrace 数据，本地，不进 git）
├── .memtrace-archive/   旧任务只读归档（本地，不进 git）
└── .omp/                OMP 项目级组件（extensions/memtrace/）
```

## 快速开始

前置提醒：OMP 已安装并可用；Python 3.10+（memtrace CLI 需要）。两条安装路径的完整细节分别以 [omp/setup.md](./omp/setup.md) 与 [template/README.md](./template/README.md) 为准，本节只给关键步骤与验证点。

### 路径 1：新设备安装主包

1. **克隆仓库**：`git clone <仓库地址> <本地目录>` 后进入目录。
   预期：目录内含 `skills/`、`memtrace/`、`template/`、`.omp/extensions/memtrace/`。
2. **配置 OMP 加载 Skill**（仓库根执行，命令自动取当前路径，勿手改成绝对路径）：

   ```bash
   # bash
   omp config set skills.customDirectories --json "[\"$(pwd)/skills\"]"
   ```

   ```powershell
   # PowerShell
   omp config set skills.customDirectories --json "[\"$($pwd.Path)/skills\"]"
   ```

   预期：命令无报错；重启 OMP 后生效。
3. **跑触发矩阵验证**：新 OMP 会话按 [tests/omp-loading.md](./tests/omp-loading.md) 执行。
   预期：8 个 Skill 列表可见，正向矩阵 8 项＋负向 2 项全过；会话出现「memtrace 任务记录已加载」。

### 路径 2：新项目接入

### 路径 2：新项目接入（bootstrap 一条命令）

1. **安装**（主包根执行，`<目标项目路径>` 替换为实际路径；纯本地复制，零网络，`--dry-run` 可先预览）：

   ```bash
   # bash
   PYTHONPATH=. python -m memtrace bootstrap <目标项目路径>
   ```

   ```powershell
   # PowerShell
   $env:PYTHONPATH="."; python -m memtrace bootstrap <目标项目路径>
   ```

   预期：报告模板、Skills（8 个）、memtrace、扩展四组新增计数与冲突数（首次应为「冲突 0」）；项目根出现 `agent-joshu/`、`.omp/`、`.agents/memtrace_config.toml`、`.memtrace/`，并自动并入根 `AGENTS.md` 标记区块与 `.gitignore` 追加。
2. **验证**：项目根开新 OMP 会话。
   预期：出现「memtrace 任务记录已加载」（无任务时安静）；`git status` 只见 `agent-joshu/`、`.omp/`、`.agents/`、`AGENTS.md` 与 `.gitignore`，`.memtrace/` 被忽略。
3. **更新**：主包组件更新后重跑同一条命令＝比对更新；项目自有内容（adr、已并入段落）永不覆盖，你改过的 kit 文件写同名 `.new` 由你决定。

### 路径 3：30 秒体验 memtrace

在主包根或任一 bootstrap 过的项目根执行（bash 形式；PowerShell 用 `$env:PYTHONPATH` 写法）：主包根用 `PYTHONPATH=.`，bootstrap 过的项目用 `PYTHONPATH=<项目>/agent-joshu`。

```bash
PYTHONPATH=. python -m memtrace create "第一个任务"
PYTHONPATH=. python -m memtrace log 22-01 "开个头" --actor user
PYTHONPATH=. python -m memtrace read 22-01
```

预期：

- `create` 输出任务摘要（目录名、id、`status: planning`、path 指向 `.memtrace/YYYY/MM/NN--slug/`）
- `log` 输出 `已追加 1 条（actor=user）→ …/wal/YYYY-MM-DD.md`
- `read` 回显同一任务的元数据、TASK.md 预览与 WAL 文件列表（看内容用 `--wal`）；任务引用可用完整目录名、短序号（如 `22-01`）、纯 slug 或 id 前缀

## Skill 库

| Skill | 触发 | 说明 |
| --- | --- | --- |
| inference-ops | 用户显式 | 推理运维：部署排障 × 性能优化（3 模式 + 10 篇方法论文档 + 知识库协议） |
| grill-me | 用户显式 | 需求盘问：把不完整想法/计划盘成可执行规格 |
| architect | 自动 | 架构：系统分析、设计、评审、技术选型 |
| python-engineering | 自动 | Python 工程实践：结构/依赖/类型/测试/工具链 |
| code-quality | 自动 | 代码质量：原则、模式、重构、测试设计 |
| deep-research | 自动 | 深度调研：来源采集、交叉验证、论断边界 |
| unslop | 自动 | 去除文本 AI 痕迹、换回人话（上游声明「必须始终应用」） |
| memtrace | 自动 | 任务过程记录：create/log/read/search/update，阶段性 WAL（变更/推翻/验证/用户纠正） |

## 多代理闭环（herdr 可用时）

```
用户需求
  → claude（study:p2）：按 Skill 设计方案/报告
  → codex（study:p3）：独立验证（只读，PASS/FAIL + 证据 + 必须修正项）
  → omp（study:p1）：修正落地执行（L2/L3 命令另行授权）
  → 产出归档（reports/ 调研目录）；可复用模式沉淀 omp/prompts/
```

- 前置探测：`test "$HERDR_ENV" = 1`；herdr 不可用时单代理照常。
- 设计稿与验证报告分别落盘（各自独立成文件），验证只读不改。
- 本工作区即由该闭环构建：01 总结(omp) → 03 设计(claude) → 04 验证(codex) → 落地(omp)。

## 维护

- 知识条目（`inference-ops` 的 `references/knowledge/`）按需生成（一场景一条目），引擎大版本发布后标 `needs-review` 复核。
- 报告解决后从 `reports/` 删除或移入对应任务材料。
- OMP 升级后重验 `skills.customDirectories`（`omp config get ... --json`），不猜键名。
- 新的长期边界决定按 `.agents/adr/README.md` 的生命周期入 ADR 目录；场景回归用 `tests/scenarios.md`。
- `template/` 内容变更时同步更新 `template/agent-joshu/VERSION`；已安装项目重跑 `bootstrap` 比对更新（见 `template/README.md`「更新」节）。

## 来源与致谢

主要的通用 Skill 与部分工作流思路来自 [ruokee-agent-kit](https://github.com/ruokee/ruokee-agent-kit)，上游采用 MIT License。本仓库在此基础上加入 `inference-ops`、`unslop`、主包与项目侧双层结构、ADR、模板、证据规范和验收脚本。第三方版权与许可文本见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。

## 许可证

本项目采用 [MIT License](./LICENSE)。
