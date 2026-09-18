# 资源耗尽

OOM、显存不足、磁盘满、文件描述符耗尽。

## 内存OOM

### 诊断

**信号**：
- Killed（exit code 137）
- dmesg：Out of memory
- 进程突然消失

**检查**：
```bash
dmesg | grep -i "out of memory"
dmesg | grep -i "killed process"
free -h  # 当前内存
journalctl -k | grep oom
```

**找出被杀进程**：
```
[ 1234.567890] Out of memory: Killed process 12345 (python) ...
```

### 预防

- 设置资源限制（cgroup, ulimit）
- 监控内存使用趋势
- 合理batch size

## GPU显存OOM

### 诊断

**信号**：
- CUDA out of memory
- RuntimeError: CUDA error
- 进程卡住无响应

**检查**：
```bash
nvidia-smi  # 当前显存使用
nvidia-smi dmon  # 实时监控
```

**估算需求**：见 perf-analysis 的 memory-and-kv-capacity.md

### 解决方向

- 减少batch size
- 减少max_seq_len
- 模型量化
- 多卡分布

## 磁盘满

### 诊断

**信号**：
- No space left on device
- 写入失败
- 日志停止

**检查**：
```bash
df -h  # 磁盘使用
du -sh /*  # 各目录占用
du -h --max-depth=1 /var/log | sort -hr  # 找大文件
```

### 常见占用

- 日志未轮转
- 模型缓存
- 临时文件未清理
- Docker镜像与容器

## 文件描述符耗尽

### 诊断

**信号**：
- Too many open files
- 无法创建新连接/文件

**检查**：
```bash
ulimit -n  # 当前限制
lsof -p <pid> | wc -l  # 进程打开的文件数
cat /proc/<pid>/limits  # 进程限制
```

### 解决

```bash
# 临时提高（当前shell）
ulimit -n 65536

# 永久（需root）
# /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
```

## 与其他文档关系

- layered-diagnosis.md：资源问题定位
- resolution-rollback-and-closure.md：资源扩容方案
