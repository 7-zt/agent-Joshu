# 容器、网络、权限

容器运行时、网络路径、文件权限、SELinux/AppArmor。

## 容器诊断

### 镜像问题

**检查**：
```bash
docker images  # 镜像列表
docker inspect <image_id>  # 详细信息
docker history <image_id>  # 构建层次
```

**常见问题**：
- 基础镜像与构建环境不匹配
- 层缓存导致旧文件残留
- multi-stage build失败

### 容器启动失败

**日志查看**：
```bash
docker logs <container_id>
docker inspect <container_id> | grep -A 20 "State"
```

**常见原因**：
- 入口命令不存在
- 配置文件缺失
- 端口冲突
- 资源限制

### Volume问题

**检查挂载**：
```bash
docker inspect <container> | grep -A 10 "Mounts"
```

**常见问题**：
- 宿主路径不存在
- 权限不匹配（uid/gid）
- 读写权限（ro vs rw）

## 网络诊断

### 端口可达性

**检查流程**：
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

**常见问题**：
- 只监听127.0.0.1 → 改为0.0.0.0
- 防火墙阻止 → iptables/firewalld规则
- Docker网络隔离 → --network host或端口映射

### DNS与服务发现

**检查**：
```bash
nslookup <service_name>
dig <service_name>
cat /etc/resolv.conf
```

## 权限问题

### 文件权限

**检查**：
```bash
ls -la <file>
stat <file>
namei -l <path>  # 逐层权限检查
```

**常见模式**：
- 容器内运行用户与文件owner不匹配
- 目录无+x权限导致无法cd
- umask导致新文件权限不足

### SELinux

**检查状态**：
```bash
getenforce  # Enforcing/Permissive/Disabled
ausearch -m avc -ts recent  # 最近的拒绝记录
```

**临时测试**（需root）：
```bash
setenforce 0  # 临时Permissive
# 测试问题是否消失
setenforce 1  # 恢复
```

**正确做法**：不长期Disable，而是配置正确的context

### AppArmor（Ubuntu/Debian）

**检查**：
```bash
aa-status
dmesg | grep apparmor
```

## 与其他文档关系

- layered-diagnosis.md：容器/系统层
- dependency-and-runtime-boundaries.md：容器运行时
