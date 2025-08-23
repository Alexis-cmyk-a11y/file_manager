# Redis 设置和使用说明

## 概述

本项目已集成Redis支持，用于提供缓存、会话存储和性能优化功能。Redis作为内存数据库，可以显著提升文件管理器的响应速度和并发处理能力。

## 功能特性

- **缓存服务**: 文件信息、目录列表等数据的智能缓存
- **会话管理**: 用户会话数据的持久化存储
- **性能监控**: 操作统计和性能指标收集
- **连接池管理**: 高效的Redis连接管理
- **自动重连**: 网络异常时的自动重连机制
- **数据序列化**: 自动处理复杂数据类型的序列化

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

在 `core/config.py` 文件中修改Redis配置：

```python
class Config:
    # Redis配置
    REDIS_HOST = 'localhost'        # Redis服务器地址
    REDIS_PORT = 6379               # Redis服务器端口
    REDIS_DB = 0                    # 使用的数据库编号
    REDIS_PASSWORD = None           # Redis密码（如果有）
    REDIS_SSL = False               # 是否使用SSL连接
    REDIS_SSL_CERT_REQS = 'none'    # SSL证书要求
    REDIS_CONNECTION_POOL_SIZE = 10  # 连接池大小
    REDIS_SOCKET_TIMEOUT = 5        # 套接字超时时间（秒）
    REDIS_SOCKET_CONNECT_TIMEOUT = 5 # 连接超时时间（秒）
    REDIS_RETRY_ON_TIMEOUT = True   # 超时时是否重试
    REDIS_HEALTH_CHECK_INTERVAL = 30 # 健康检查间隔（秒）
```

### 配置参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `REDIS_HOST` | localhost | Redis服务器地址 |
| `REDIS_PORT` | 6379 | Redis服务器端口 |
| `REDIS_DB` | 0 | 使用的数据库编号 |
| `REDIS_PASSWORD` | None | Redis密码（如果有） |
| `REDIS_SSL` | False | 是否使用SSL连接 |
| `REDIS_CONNECTION_POOL_SIZE` | 10 | 连接池大小 |
| `REDIS_SOCKET_TIMEOUT` | 5 | 套接字超时时间（秒） |
| `REDIS_RETRY_ON_TIMEOUT` | True | 超时时是否重试 |

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

# 检查状态
sudo systemctl status redis
```

## 使用示例

### 1. 基本Redis操作

```python
from services.redis_service import get_redis_service

# 获取Redis服务实例
redis_service = get_redis_service()

# 设置键值对
redis_service.set('key', 'value', ex=3600)  # 1小时过期

# 获取值
value = redis_service.get('key', default='default_value')

# 删除键
redis_service.delete('key')

# 检查键是否存在
exists = redis_service.exists('key')
```

### 2. 缓存服务使用

```python
from services.cache_service import get_cache_service

# 获取缓存服务实例
cache_service = get_cache_service()

# 缓存文件信息
file_info = {'name': 'test.txt', 'size': 1024, 'modified': '2024-01-01'}
cache_service.cache_file_info('/path/to/file', file_info, ttl=1800)  # 30分钟

# 获取缓存的文件信息
cached_info = cache_service.get_cached_file_info('/path/to/file')

# 缓存目录列表
dir_listing = [{'name': 'file1.txt'}, {'name': 'file2.txt'}]
cache_service.cache_directory_listing('/path/to/dir', dir_listing)

# 使缓存失效
cache_service.invalidate_file_cache('/path/to/file')
cache_service.invalidate_directory_cache('/path/to/dir')
```

## API接口

### Redis状态检查

```bash
# 获取Redis状态
GET /api/system/redis/status

# 测试Redis连接
POST /api/system/redis/test

# 获取Redis键列表
GET /api/system/redis/keys?pattern=*

# 清空Redis数据库
POST /api/system/redis/clear
```

## 监控和维护

### 1. 连接状态监控

应用启动时会自动检查Redis连接状态，并在日志中记录连接结果。如果Redis不可用，系统会自动降级到内存存储。

### 2. 性能监控

Redis服务提供以下监控指标：
- 连接状态
- 内存使用情况
- 连接客户端数量
- 运行时间
- 缓存命中率

### 3. 日志记录

所有Redis操作都会记录到应用日志中，包括：
- 连接状态变化
- 操作成功/失败
- 错误详情
- 性能指标

## 故障排除

### 常见问题

1. **连接失败**
   - 检查Redis服务是否启动：`redis-cli ping`
   - 验证主机地址和端口配置
   - 检查防火墙设置

2. **认证失败**
   - 确认Redis密码设置
   - 检查配置文件中的密码配置

3. **性能问题**
   - 调整连接池大小
   - 优化缓存策略
   - 监控内存使用

### 调试命令

```bash
# 检查Redis服务状态
redis-cli ping

# 查看Redis信息
redis-cli info

# 监控Redis命令
redis-cli monitor

# 查看内存使用
redis-cli info memory
```

## 最佳实践

1. **合理设置TTL**: 根据数据更新频率设置合适的过期时间
2. **错误处理**: 始终检查操作返回值并处理异常
3. **监控告警**: 设置Redis监控和告警机制
4. **备份策略**: 定期备份重要数据
5. **优雅降级**: 当Redis不可用时，系统自动降级到内存存储

## 自动降级机制

如果Redis服务不可用，系统会自动降级到内存存储：
- 缓存功能仍然可用，但数据只在应用运行期间保存
- 不影响核心文件管理功能
- 应用启动和运行都不会受到影响

这确保了即使没有Redis，文件管理系统依然可以正常工作。