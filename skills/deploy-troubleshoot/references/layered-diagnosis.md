# 分层诊断

硬件→驱动→系统→容器→依赖→服务→应用的逐层排查方法。

## 层次模型

```
应用层      │ 业务逻辑、配置错误、资源耗尽
  ↓ 
服务层      │ 启动失败、端口占用、健康检查
  ↓
依赖层      │ 包版本冲突、导入失败、库不兼容
  ↓
容器/运行时 │ 镜像问题、volume、网络、权限
  ↓
系统层      │ OS配置、文件系统、进程限制
  ↓
驱动层      │ CUDA/驱动版本、加载失败
  ↓
硬件层      │ GPU可见性、内存、PCIe
```

## 判断顺序

**自底向上**（推荐默认）：
- 从硬件开始逐层向上
- 每层健康才进入上层
- 适合：无明确报错、新环境、首次部署

**自顶向下**（有明确信号时）：
- 从报错信号直接定位层次
- 快速收敛
- 适合：有清晰错误信息

**夹逼**（复杂问题）：
- 同时从两端检查
- 找到断裂层

## 每层检查清单

### 硬件层

**检查命令**（L0）：
```bash
nvidia-smi  # GPU可见性与状态
lspci | grep -i nvidia  # PCIe设备
free -h  # 内存
df -h  # 磁盘
```

**健康标准**：
- GPU被OS识别
- 无硬件错误
- 显存/内存充足

**常见问题**：
- GPU不可见
- PCIe降速（x8 vs x16）
- 显存ECC错误

### 驱动层

**检查命令**：
```bash
nvidia-smi  # 驱动版本
cat /proc/driver/nvidia/version
nvcc --version  # CUDA版本
```

**健康标准**：
- 驱动版本与CUDA兼容
- 能查询GPU信息
- 无驱动崩溃日志

**常见问题**：
- driver mismatch
- CUDA runtime vs driver版本不匹配
- 驱动未加载

### 系统层

**检查命令**：
```bash
uname -a  # OS版本
ulimit -a  # 进程限制
dmesg | tail -50  # 内核日志
journalctl -xe  # 系统日志
```

**健康标准**：
- 无OOM killer记录
- 文件描述符限制足够
- 无SELinux/AppArmor阻止

**常见问题**：
- ulimit过低
- 权限不足
- 内核OOM

### 容器/运行时层

**检查命令**：
```bash
docker --version / podman --version
docker inspect <container>
docker run --rm --gpus all nvidia/cuda nvidia-smi  # GPU容器测试
（具体以当前 NVIDIA Container Toolkit 版本文档为准）
```

**健康标准**：
- NVIDIA Container Toolkit安装
- GPU在容器内可见
- volume正确挂载

**常见问题**：
- runtime=nvidia未配置
- volume路径错误
- 网络隔离

### 依赖层

**检查命令**：
```bash
python --version
pip list | grep <关键包>
pip show <包名>  # 详细版本与依赖
python -c "import torch; print(torch.cuda.is_available())"
```

**健康标准**：
- Python版本匹配
- 关键包已安装且版本兼容
- 能导入核心库

**常见问题**：
- 版本冲突
- 缺少依赖
- ABI不兼容

### 服务层

**检查命令**：
```bash
ps aux | grep <服务名>
netstat -tuln | grep <端口>
curl localhost:<端口>/health
systemctl status <服务>  # systemd服务
```

**健康标准**：
- 进程运行
- 端口监听
- 健康检查通过

**常见问题**：
- 启动失败
- 端口被占用
- 配置文件错误

### 应用层

**检查**：
- 应用日志
- 配置参数
- 业务逻辑错误

## 停止条件

**找到断裂层**：某层不健康，下层健康→锁定该层

**全层健康但问题仍在**：可能是负载、时序、外部依赖问题

## 与其他文档关系

- evidence-collection.md：每层证据采集方法
- reproduction-and-bisect.md：定位后的验证
