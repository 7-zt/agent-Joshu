# 证据收集

命令五元组、日志提取、配置导出、脱敏规则。

## 命令五元组

每条诊断命令记录：

1. **命令文本**：完整命令行
2. **执行环境**：用户、主机、路径
3. **退出码**：0=成功，非0=失败
4. **输出摘要**：关键行，不是完整dump
5. **时间戳**：执行时间

**示例**：
```
命令：nvidia-smi
环境：user@host:/home/user
退出码：0
输出：Driver 525.105.17, CUDA 12.0, 1x A100-80GB
时间：2026-09-17 14:30:25
```

## 日志提取

**原则**：
- 完整错误上下文（前后各5-10行）
- 保留时间戳
- 标注日志来源（路径、服务名）

**提取方法**：
```bash
# 查找ERROR并带上下文
grep -A 10 -B 5 "ERROR" /var/log/service.log | tail -50

# 特定时间段
journalctl --since "14:00" --until "14:30" -u myservice.service

# 实时跟踪
tail -f /var/log/service.log
```

**关键字段**：
- 时间戳
- 日志级别（ERROR/WARN/INFO）
- 错误类型（异常类名、错误码）
- 堆栈跟踪（如有）

## 配置导出

**导出什么**：
- 服务配置文件（YAML/JSON/TOML）
- 环境变量（`env`）
- 启动参数
- 资源限制（`ulimit -a`）

**脱敏**：
- 密钥/token → `<REDACTED>`
- 内网IP/域名 → `<INTERNAL_IP>`或保留最后一段
- 用户名 → `<USER>`（除非相关）

**示例**：
```yaml
# config.yaml (sanitized)
api_key: <REDACTED>
model_path: /models/llama-7b
max_batch_size: 32
gpu_ids: [0, 1]
internal_endpoint: http://<INTERNAL_IP>:8080
```

## 环境快照模板

见 environment-snapshot.md，此处强调采集规则：
- 版本信息用命令获取，不凭记忆
- 多次运行同一命令可能结果不同（如`nvidia-smi`），标注时间
- 容器环境内外都要采集

## 与其他文档关系

- environment-snapshot.md：具体字段清单
- layered-diagnosis.md：每层的证据采集点
