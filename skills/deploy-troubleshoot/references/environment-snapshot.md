# 环境快照与命令记录

排障与性能测量共用的环境证据标准：环境信息必须可追溯，命令执行必须可复盘。

## 1. 环境快照最小字段

| 类别 | 字段 | 采集方式 |
| --- | --- | --- |
| 时间 | 快照采集时间（含时区） | `date -Is` 或等价 |
| 硬件 | GPU 型号/数量/拓扑、CPU、内存、磁盘 | `nvidia-smi`、`nvidia-smi topo -m`、`lscpu`、`free -h` |
| 驱动与 CUDA | 驱动版本、CUDA runtime/toolkit 版本 | `nvidia-smi`（驱动/CUDA 版本行）、`nvcc --version`、`nvidia-container-cli --version` |
| 系统 | 发行版与版本、内核 | `cat /etc/os-release`、`uname -r` |
| 容器（如适用） | runtime、镜像 digest、启动参数、挂载、网络 | `docker info`、`docker inspect`、`docker images --digests` |
| Python（如适用） | 解释器版本与路径、虚拟环境、关键包及版本 | `python --version`、`which python`、`pip list` 或锁文件 |
| 推理引擎（如适用） | 版本或 commit、关键启动参数 | 引擎 `--version` / 服务端启动日志 / 包版本 |
| 关键环境变量 | 影响行为的变量（`CUDA_VISIBLE_DEVICES` 等） | `env` 过滤 |

按问题相关性裁剪；无关类别写「不适用」，不编造。

## 2. 验证命令记录

每条用于下结论的命令记录五元组：**命令文本、退出码、标准输出（关键部分）、标准错误、执行位置**（哪台机/容器内）。口头转述「跑过某命令结果是好的」不构成证据。

## 3. 脱敏规则

写入报告前必须脱敏：API token、密钥、密码、私有 IP/主机名（可保留网段）、路径中的用户名（按需）。原则：脱敏不改变技术含义。无法既脱敏又保真时，该内容留在本地，报告中写「含敏感信息，见本地归档路径」。

## 4. 快照归档

快照与排查/测量记录一起归档到任务材料或报告目录，标注采集时间。环境变更（升级驱动、换镜像）后旧快照作废，需重采。
