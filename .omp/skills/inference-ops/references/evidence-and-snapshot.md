# 证据与快照

排障与性能测量共用的证据标准：环境信息必须可追溯，命令执行必须可复盘。证据的最小单位是命令五元组；环境事实的载体是环境快照。

## 命令五元组

每条用于下结论的命令记录五元组：**命令文本、退出码、标准输出（关键部分）、标准错误、执行位置**（哪台机/容器内）。口头转述「跑过某命令结果是好的」不构成证据。

**示例**：

```text
命令：nvidia-smi
环境：user@host:/home/<user>（容器内/宿主机标注）
退出码：0
输出：Driver 525.105.17, CUDA 12.0, 1x A100-80GB
时间：2026-09-17 14:30:25
```

## 日志提取

**原则**：
- 完整错误上下文（前后各 5-10 行）
- 保留时间戳
- 标注日志来源（路径、服务名）

**提取方法**：

```bash
# 查找 ERROR 并带上下文
grep -A 10 -B 5 "ERROR" /var/log/service.log | tail -50

# 特定时间段
journalctl --since "14:00" --until "14:30" -u myservice.service

# 实时跟踪
tail -f /var/log/service.log
```

**关键字段**：时间戳、日志级别（ERROR/WARN/INFO）、错误类型（异常类名、错误码）、堆栈跟踪（如有）。

## 配置导出

**导出什么**：服务配置文件（YAML/JSON/TOML）、环境变量（`env`）、启动参数、资源限制（`ulimit -a`）。导出内容按脱敏规则处理后写入报告。

## 环境快照最小字段

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

采集规则：

- 版本信息用命令获取，不凭记忆；多次运行同一命令可能结果不同（如 `nvidia-smi`），标注时间。
- 按问题相关性裁剪；无关类别写「不适用」，不编造。
- 容器环境内外都要采集（如适用）。

## 脱敏规则

写入报告前必须脱敏：API token、密钥、密码、私有 IP/主机名（可保留网段）、路径中的用户名（按需）。原则：脱敏不改变技术含义。

**示例**：

```yaml
# config.yaml (sanitized)
api_key: <REDACTED>
model_path: /models/llama-7b
max_batch_size: 32
gpu_ids: [0, 1]
internal_endpoint: http://<INTERNAL_IP>:8080
```

无法既脱敏又保真时，该内容留在本地，报告中写「含敏感信息，见本地归档路径」。

## 快照归档

快照与排查/测量记录一起归档到任务材料或报告目录，标注采集时间。环境变更（升级驱动、换镜像）后旧快照作废，需重采。

## 与其他文档关系

- [layered-diagnosis](./layered-diagnosis.md)：每层的证据采集点
- [benchmark-protocol](./benchmark-protocol.md)：性能测量的环境记录要求
- [reporting](./reporting.md)：证据进入报告的脱敏与引用规范
