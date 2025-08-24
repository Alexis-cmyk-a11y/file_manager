# Redis 设置和使用说明

## 概述

本项目已集成Redis支持，用于提供缓存、会话存储和性能优化功能。Redis作为内存数据库，可以显著提升文件管理器的响应速度和并发处理能力。

## 功能特性

- **缓存服务**: 文件信息、目录列表等数据的智能缓存
- **会话管理**: 用户会话数据的持久化存储
- **性能监控**: 操作统计和性能指标收集
- **连接池管理**: 高效的Redis连接管理

## 安装要求

### 1. 安装Redis服务器

#### Windows
```bash
# 使用Chocolatey安装
choco install redis-64

# 或下载Windows版本
# https://github.com/microsoftarchive/redis/releases
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install redis-server
```

#### macOS
```bash
# 使用Homebrew安装
brew install redis
```

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 配置文件设置

在 `config.yaml` 文件中修改Redis配置：

```yaml
redis:
  host: "localhost"
  port: 6379
  db: 0
  password: null
  ssl: false
  
  pool_config:
    max_connections: 20
    retry_on_timeout: true
    socket_keepalive: true
    health_check_interval: 30
```

### 环境变量配置

```bash
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password
```

## 启动Redis服务

### Windows
```bash
# 启动Redis服务
redis-server

# 或作为Windows服务启动
redis-server --service-install
redis-server --service-start
```

### Linux/macOS
```bash
# 启动Redis服务
sudo systemctl start redis

# 或手动启动
redis-server
```

## 验证连接

### 1. 命令行测试
```bash
redis-cli ping
# 应该返回: PONG
```

### 2. 应用内测试
访问健康检查端点：
```bash
curl http://localhost:8888/api/health
```

## 故障排除

### 常见问题

**Q: Redis连接失败**
```bash
# 检查Redis服务状态
redis-cli ping

# 检查端口是否被占用
netstat -an | grep 6379
```

**Q: 权限问题**
```bash
# 检查Redis配置文件
sudo nano /etc/redis/redis.conf

# 确保bind设置正确
bind 127.0.0.1
```

**Q: 内存不足**
```bash
# 检查Redis内存使用
redis-cli info memory

# 设置最大内存
redis-cli config set maxmemory 100mb
```

## 性能优化建议

1. **连接池**: 使用连接池管理连接
2. **持久化**: 根据需求配置RDB或AOF
3. **内存管理**: 设置合理的内存限制
4. **网络优化**: 使用本地连接减少延迟

## 监控和维护

### 健康检查
- 应用内健康检查: `/api/health`
- Redis状态监控: `/api/cache/status`

### 日志查看
```bash
# 查看Redis日志
tail -f /var/log/redis/redis-server.log

# 使用项目日志管理工具
python scripts/log_manager.py
```