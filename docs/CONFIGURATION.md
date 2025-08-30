# 配置文件系统文档

## 概述

文件管理系统使用基于YAML的配置文件系统，支持多环境配置管理。

## 配置目录结构

```
config/
├── config.yaml              # 主配置文件
├── environment.txt           # 环境配置文件
├── development.yaml         # 开发环境配置
├── production.yaml          # 生产环境配置
└── tencent_cloud.py        # 腾讯云配置
```

## 快速配置

### 1. 环境切换

编辑 `config/environment.txt` 文件：
```
development  # 或 production
```

### 2. 基本配置

**config.yaml** - 主配置文件：
```yaml
app:
  name: "文件管理系统"
  version: "2.0.0"

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

### 3. 环境特定配置

**development.yaml:**
```yaml
debug: true
log_level: DEBUG
server:
  host: "127.0.0.1"
  port: 8888
```

**production.yaml:**
```yaml
debug: false
log_level: WARNING
server:
  host: "0.0.0.0"
  port: 8888
```

## 配置管理

### 验证配置
```bash
python scripts/validate_config.py
```

### 管理配置
```bash
python scripts/manage_config.py info      # 显示配置信息
python scripts/manage_config.py backup    # 创建备份
python scripts/manage_config.py restore   # 恢复备份
```

## 最佳实践

1. **环境分离**: 开发环境启用调试，生产环境关闭调试
2. **敏感信息**: 不要在配置文件中硬编码密码
3. **配置备份**: 定期备份配置文件
4. **版本控制**: 将配置文件纳入版本控制

## 故障排除

- 检查YAML语法和文件编码（UTF-8）
- 确认环境文件内容正确
- 验证配置项的数据类型和范围
