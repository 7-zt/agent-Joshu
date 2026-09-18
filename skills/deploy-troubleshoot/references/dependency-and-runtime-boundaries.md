# 依赖与运行时边界

Python虚拟环境、包解析、运行时库、ABI兼容。

## Python依赖边界

### 虚拟环境隔离

**类型**：
- venv/virtualenv：标准Python隔离
- conda：包管理+环境管理
- poetry/pipenv：锁定依赖版本
- Docker：最强隔离

**检查当前环境**：
```bash
which python  # Python路径
pip --version  # pip关联的Python
pip list  # 已安装包
```

### 版本冲突诊断

**常见模式**：
- A依赖 torch>=2.0, B依赖 torch<2.0 → 无解
- 安装时无报错，import时失败 → ABI不兼容

**诊断**：
```bash
pip show <包名>  # 查看依赖树
pip check  # 检查冲突（不总能发现）
python -c "import <module>"  # 直接测试导入
```

### 运行时库依赖

**CUDA库**：
- CUDA runtime (libcudart.so)
- cuDNN
- cuBLAS/cuSPARSE

**检查**：
```bash
ldd $(python -c "import torch; print(torch.__file__.replace('__init__.py', 'lib/libtorch_cuda.so'))")
```

**常见问题**：
- 找不到 libcudart.so.12 → CUDA版本不匹配
- 找不到 libcudnn.so → cuDNN未安装
- 版本mismatch → torch编译时的CUDA与运行时不同

## 容器运行时边界

### GPU容器支持

**要求**：
- NVIDIA Container Toolkit
- runtime配置

**检查**：
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

失败原因：
- --gpus参数不识别 → runtime未配置
- 容器内看不到GPU → toolkit未装
- 版本不匹配 → 驱动太老

### volume与权限

**常见问题**：
- 容器内路径不存在 → volume未正确挂载
- Permission denied → 文件权限或SELinux
- 数据不同步 → volume cache或mount类型

## 系统库边界

**glibc版本**：
```bash
ldd --version
```

**编译环境vs运行环境**：
- 在新系统编译，老系统运行 → GLIBC版本不足
- 解决：用老系统编译 或 静态链接 或 容器

## 与其他文档关系

- layered-diagnosis.md：依赖层与运行时层
- container-network-permission.md：容器边界问题
