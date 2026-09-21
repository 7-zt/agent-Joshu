# OMP 加载验证

用户自验步骤，确认 workflow Skill 在 OMP 中正确加载。

## 前提条件

- OMP 已安装（测试版本：18.2.3）
- 已在 OMP 配置中添加 skills 目录（见 omp/setup.md）

## 验证步骤

### 1. 重启 OMP

重启 OMP 应用，确保配置生效。

### 2. 验证 Skill 被发现

在 OMP 中输入 `/skills` 或查看 Skills 列表，应看到：

- ✓ inference-ops

**如果未显示**：
- 检查 OMP 配置中的 `skills.customDirectories` 路径是否正确
- 检查路径是否为绝对路径
- 查看 OMP 日志是否有加载错误

### 3. 验证 Skill 可调用

```
/skill:inference-ops
```
预期：进入 inference-ops Skill，收到模式选择或引导信息

**如果无法调用**：
- 检查 `agents/openai.yaml` 文件是否存在
- 检查 YAML 格式是否正确
- 检查 `disable-model-invocation: true` 是否设置

### 4. 验证 Skill 内部链接

在 Skill 会话中，如果 Skill 引用了内部文档（如 benchmark-protocol），
应能正确加载，不应报告文件未找到。

### 5. 验证组件自包含

尝试将 `skills/inference-ops/` 目录单独复制到另一位置，
添加到 OMP 配置，应仍能正常加载和使用。

## 结果记录

| 项目 | 状态 | 备注 |
| --- | --- | --- |
| Skill 列表显示 | ☐ 通过 ☐ 失败 | |
| inference-ops 可调用 | ☐ 通过 ☐ 失败 | |
| 内部链接正常 | ☐ 通过 ☐ 失败 | |
| Skill 可独立使用 | ☐ 通过 ☐ 失败 | |

## 故障排查

如果加载失败，检查：
1. 路径配置是否正确（绝对路径）
2. SKILL.md 的 frontmatter 格式是否正确
3. agents/openai.yaml 是否存在且格式正确
4. OMP 版本是否支持自定义 Skills 目录
5. 运行 `tools/check-workflow.ps1` 检查文件结构

## 注意

- 本验证不需要真实执行 GPU 任务
- 重点验证加载与触发机制，不验证 Skill 功能完整性
- Skill 功能完整性由 tests/scenarios.md 的场景卡验证
