# 部署常见故障域

分层诊断（见 [layered-diagnosis](./layered-diagnosis.md)）锁定层次后，三个高频故障域的深入检查：依赖与运行时边界、容器/网络/权限、资源耗尽。

## 一、依赖与运行时边界

Python 虚拟环境、包解析、运行时库、ABI 兼容。

### Python 依赖边界

**虚拟环境隔离类型**：venv/virtualenv（标准隔离）、conda（包管理+环境管理）、poetry/pipenv（锁定依赖版本）、Docker（最强隔离）。

**检查当前环境**：

```bash
which python  # Python路径
pip --version  # pip关联的Python
pip list  # 已安装包
```

**版本冲突诊断**：

- 常见模式：A 依赖 torch>=2.0, B 依赖 torch<2.0 → 无解；安装时无报错，import 时失败 → ABI 不兼容。

```bash
pip show <包名>  # 查看依赖树
pip check  # 检查冲突（不总能发现）
python -c "import <module>"  # 直接测试导入
```

### 运行时库依赖

**CUDA 库**：CUDA runtime (libcudart.so)、cuDNN、cuBLAS/cuSPARSE。

**检查**：

```bash
ldd $(python -c "import torch; print(torch.__file__.replace('__init__.py', 'lib/libtorch_cuda.so'))")
```

**常见问题**：找不到 libcudart.so.12 → CUDA 版本不匹配；找不到 libcudnn.so → cuDNN 未安装；版本 mismatch → torch 编译时的 CUDA 与运行时不同。

### 容器运行时边界

**GPU 容器支持要求**：NVIDIA Container Toolkit + runtime 配置。

```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

失败原因：`--gpus` 参数不识别 → runtime 未配置；容器内看不到 GPU → toolkit 未装；版本不匹配 → 驱动太老。

**volume 与权限**：容器内路径不存在 → volume 未正确挂载；Permission denied → 文件权限或 SELinux；数据不同步 → volume cache 或 mount 类型。

### 系统库边界

**glibc 版本**：`ldd --version`。编译环境 vs 运行环境：在新系统编译、老系统运行 → GLIBC 版本不足。解决：用老系统编译，或静态链接，或容器。

## 二、容器、网络、权限

### 容器诊断

**镜像问题**：

```bash
docker images  # 镜像列表
docker inspect <image_id>  # 详细信息
docker history <image_id>  # 构建层次
```

常见问题：基础镜像与构建环境不匹配、层缓存导致旧文件残留、multi-stage build 失败。

**容器启动失败**：

```bash
docker logs <container_id>
docker inspect <container_id> | grep -A 20 "State"
```

常见原因：入口命令不存在、配置文件缺失、端口冲突、资源限制。

**Volume 问题**：

```bash
docker inspect <container> | grep -A 10 "Mounts"
```

常见问题：宿主路径不存在、权限不匹配（uid/gid）、读写权限（ro vs rw）。

### 网络诊断

**端口可达性检查流程**：

```bash
# 1. 服务是否监听
netstat -tuln | grep <port>
ss -tuln | grep <port>

# 2. 本地可达
curl localhost:<port>
telnet localhost <port>

# 3. 容器网络
docker exec <container> curl localhost:<port>

# 4. 宿主外部可达
curl <host_ip>:<port>
```

常见问题：只监听 127.0.0.1 → 改为 0.0.0.0；防火墙阻止 → iptables/firewalld 规则；Docker 网络隔离 → `--network host` 或端口映射。

**DNS 与服务发现**：

```bash
nslookup <service_name>
dig <service_name>
cat /etc/resolv.conf
```

### 权限问题

**文件权限**：

```bash
ls -la <file>
stat <file>
namei -l <path>  # 逐层权限检查
```

常见模式：容器内运行用户与文件 owner 不匹配；目录无 +x 权限导致无法 cd；umask 导致新文件权限不足。

**SELinux**：

```bash
getenforce  # Enforcing/Permissive/Disabled
ausearch -m avc -ts recent  # 最近的拒绝记录
```

临时测试（需 root）：`setenforce 0` → 测试问题是否消失 → `setenforce 1` 恢复。正确做法：不长期 Disable，配置正确的 context。

**AppArmor（Ubuntu/Debian）**：

```bash
aa-status
dmesg | grep apparmor
```

## 三、资源耗尽

### 内存 OOM

**信号**：Killed（exit code 137）、dmesg 有 Out of memory、进程突然消失。

**检查**：

```bash
dmesg | grep -i "out of memory"
dmesg | grep -i "killed process"
free -h  # 当前内存
journalctl -k | grep oom
```

**找出被杀进程**：`[ 1234.567890 ] Out of memory: Killed process 12345 (python) ...`

**预防**：设置资源限制（cgroup, ulimit）、监控内存使用趋势、合理 batch size。

### GPU 显存 OOM

**信号**：CUDA out of memory、RuntimeError: CUDA error、进程卡住无响应。

**检查**：

```bash
nvidia-smi  # 当前显存使用
nvidia-smi dmon  # 实时监控
```

**估算需求**：见 [perf-topics](./perf-topics.md) 的显存与 KV cache 一节。

**解决方向**：减少 batch size、减少 max_seq_len、模型量化、多卡分布。

### 磁盘满

**信号**：No space left on device、写入失败、日志停止。

**检查**：

```bash
df -h  # 磁盘使用
du -sh /*  # 各目录占用
du -h --max-depth=1 /var/log | sort -hr  # 找大文件
```

**常见占用**：日志未轮转、模型缓存、临时文件未清理、Docker 镜像与容器。

### 文件描述符耗尽

**信号**：Too many open files、无法创建新连接/文件。

**检查**：

```bash
ulimit -n  # 当前限制
lsof -p <pid> | wc -l  # 进程打开的文件数
cat /proc/<pid>/limits  # 进程限制
```

**解决**：

```bash
# 临时提高（当前shell）
ulimit -n 65536

# 永久（需root）：/etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
```

## 与其他文档关系

- [layered-diagnosis](./layered-diagnosis.md)：定位方法与解决收尾
- [perf-topics](./perf-topics.md)：显存容量估算与量化
- [evidence-and-snapshot](./evidence-and-snapshot.md)：证据采集
