# 配置文件系统文档

## 概述

文件管理系统使用基于YAML的配置文件系统，完全替代了环境变量，提供了更灵活、更强大的配置管理能力。

## 配置目录结构

```
config/
├── config.yaml              # 主配置文件
├── environment.txt           # 环境配置文件
├── development.yaml         # 开发环境特定配置
├── production.yaml          # 生产环境特定配置
├── testing.yaml            # 测试环境特定配置
├── app.yaml                # 旧版配置文件（兼容性）
├── tencent_cloud.py        # 腾讯云配置
├── tencent_cloud.template.py # 腾讯云配置模板
└── backups/                # 配置备份目录
```

## 配置文件说明

### 1. 主配置文件 (config.yaml)

主配置文件包含所有配置项的基础定义，支持多环境配置。

```yaml
# 应用基础配置
app:
  name: "文件管理系统"
  version: "2.0.0"
  description: "现代化的文件管理系统"

# 环境配置
environments:
  development:
    debug: true
    server:
      host: "127.0.0.1"
      port: 8888
  production:
    debug: false
    server:
      host: "0.0.0.0"
      port: 8888

# 数据库配置
database:
  mysql:
    host: "localhost"
    port: 3306
    database: "file_manager"
    username: "root"
    password: "password"
  redis:
    host: "localhost"
    port: 6379
```

### 2. 环境配置文件 (environment.txt)

指定当前运行环境，可选值：`development`、`production`、`testing`

```
development
```

### 3. 环境特定配置文件

每个环境可以有特定的配置文件，覆盖主配置中的相应设置。

**development.yaml:**
```yaml
debug: true
log_level: DEBUG
server:
  host: "127.0.0.1"
  port: 8888
features:
  enable_debug_toolbar: true
```

**production.yaml:**
```yaml
debug: false
log_level: WARNING
server:
  host: "0.0.0.0"
  port: 8888
features:
  enable_debug_toolbar: false
```

## 配置项详解

### 应用配置 (app)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| name | string | "文件管理系统" | 应用名称 |
| version | string | "2.0.0" | 应用版本 |
| description | string | "现代化的文件管理系统" | 应用描述 |
| author | string | "File Manager Team" | 作者 |
| contact | string | "support@filemanager.local" | 联系方式 |

### 服务器配置 (server)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| host | string | "127.0.0.1" | 服务器地址 |
| port | int | 8888 | 服务器端口 |
| workers | int | 1 | 工作进程数 |
| timeout | int | 30 | 超时时间（秒） |

### 数据库配置 (database)

#### MySQL配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| host | string | "localhost" | 数据库主机 |
| port | int | 3306 | 数据库端口 |
| database | string | "file_manager" | 数据库名 |
| username | string | "root" | 用户名 |
| password | string | "" | 密码 |
| charset | string | "utf8mb4" | 字符集 |

#### Redis配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| host | string | "localhost" | Redis主机 |
| port | int | 6379 | Redis端口 |
| db | int | 0 | 数据库编号 |
| password | string | null | 密码 |

### 安全配置 (security)

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| secret_key | string | null | 密钥（自动生成） |
| session_timeout | int | 3600 | 会话超时（秒） |
| rate_limit | string | "100 per minute" | 速率限制 |
| jwt_expiration | int | 86400 | JWT过期时间（秒） |

### 前端配置 (frontend)

#### 主题配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| primary_color | string | "#4a6fa5" | 主色调 |
| secondary_color | string | "#6c8ebf" | 次要色调 |
| background_color | string | "#ffffff" | 背景色 |
| text_color | string | "#333333" | 文字色 |

#### 功能配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| default_view | string | "list" | 默认视图模式 |
| page_size | int | 50 | 每页显示数量 |
| enable_drag_drop | bool | true | 启用拖拽上传 |
| enable_preview | bool | true | 启用文件预览 |

## 配置管理工具

### 1. 配置验证

验证配置文件的正确性：

```bash
python scripts/validate_config.py
```

### 2. 配置管理

管理配置文件，包括备份、恢复、导入导出等：

```bash
# 显示配置信息
python scripts/manage_config.py info

# 创建配置备份
python scripts/manage_config.py backup

# 列出所有备份
python scripts/manage_config.py list

# 恢复配置备份
python scripts/manage_config.py restore backup_name

# 导出配置
python scripts/manage_config.py export --format json

# 导入配置
python scripts/manage_config.py import config_file.yaml

# 清理旧备份
python scripts/manage_config.py cleanup --keep 10
```

## 环境切换

### 方法1：修改环境文件

编辑 `config/environment.txt` 文件：

```
production
```

### 方法2：使用配置管理工具

```bash
# 备份当前配置
python scripts/manage_config.py backup

# 切换到生产环境配置
python scripts/manage_config.py restore production_config_backup
```

## 配置热重载

系统支持配置热重载，修改配置文件后无需重启应用：

```python
from core.config_manager import config_manager

# 重新加载配置
if config_manager.reload_config():
    print("配置已更新")
else:
    print("配置无变化")
```

## 配置验证

### 自动验证

系统启动时会自动验证配置的有效性：

- 检查必需配置项
- 验证数据类型
- 检查配置范围
- 验证环境配置

### 手动验证

```bash
# 验证所有配置文件
python scripts/validate_config.py

# 验证特定配置文件
python -c "
import yaml
from pathlib import Path
config = yaml.safe_load(Path('config/config.yaml').read_text())
print('配置验证通过')
"
```

## 最佳实践

### 1. 环境分离

- 开发环境：启用调试功能，降低安全限制
- 生产环境：关闭调试功能，启用安全限制
- 测试环境：模拟生产环境，但使用测试数据

### 2. 敏感信息管理

- 不要在配置文件中硬编码密码
- 使用环境特定的配置文件管理敏感信息
- 定期轮换密钥和密码

### 3. 配置备份

- 定期备份配置文件
- 在重大更改前创建备份
- 保留多个版本的备份

### 4. 配置版本控制

- 将配置文件纳入版本控制
- 使用模板文件管理不同环境的配置
- 记录配置变更历史

## 故障排除

### 常见问题

1. **配置加载失败**
   - 检查YAML语法
   - 验证文件编码（UTF-8）
   - 检查文件权限

2. **环境配置不生效**
   - 确认环境文件内容正确
   - 检查环境特定配置文件是否存在
   - 验证配置合并逻辑

3. **配置验证失败**
   - 检查必需配置项
   - 验证数据类型和范围
   - 查看详细错误信息

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查配置加载过程
from core.config_manager import config_manager
print(f"当前环境: {config_manager.environment}")
print(f"配置数据: {config_manager.config_data}")
```

## 迁移指南

### 从环境变量迁移

1. 创建配置文件结构
2. 将环境变量值转换为配置文件
3. 更新应用代码使用配置管理器
4. 测试配置加载
5. 移除环境变量依赖

### 从旧版配置迁移

1. 备份旧配置文件
2. 创建新的配置文件结构
3. 迁移配置项到新结构
4. 验证配置正确性
5. 更新应用代码

## 扩展配置

### 添加新配置项

1. 在配置文件中添加新配置
2. 在配置管理器中添加相应的getter方法
3. 更新配置验证逻辑
4. 添加配置文档

### 自定义配置验证

```python
def custom_config_validator(config_data):
    """自定义配置验证器"""
    errors = []
    
    # 验证自定义规则
    if 'custom_setting' in config_data:
        value = config_data['custom_setting']
        if not isinstance(value, str):
            errors.append("custom_setting必须是字符串类型")
    
    return len(errors) == 0, errors
```

## 总结

配置文件系统提供了：

- ✅ 多环境配置支持
- ✅ 配置热重载
- ✅ 自动配置验证
- ✅ 配置备份和恢复
- ✅ 灵活的配置管理
- ✅ 完整的文档支持

通过合理使用配置文件系统，可以大大简化应用部署和配置管理，提高系统的可维护性和可靠性。
