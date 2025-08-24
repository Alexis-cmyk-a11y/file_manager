# 🚀 文件管理系统技术指南

## 📋 概述

本文档提供文件管理系统的完整技术指南，包括数据库设置、缓存配置、性能优化和部署说明。

## 🗄️ 数据库设置

### MySQL配置

#### 环境要求
- **MySQL**: 5.7+ (推荐8.0+)
- **Python依赖**: `pymysql==1.1.0`, `sqlalchemy==2.0.23`

#### 快速配置
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python scripts/init_database.py
```

#### 配置文件设置
在 `config.yaml` 中配置MySQL：

```yaml
mysql:
  host: "localhost"
  port: 3306
  database: "file_manager"
  username: "root"
  password: "your_password"
  charset: "utf8mb4"
  
  pool_config:
    max_connections: 20
    min_connections: 5
    pool_recycle: 3600
    pool_pre_ping: true
```

### Redis配置

#### 环境要求
- **Redis**: 推荐安装（可选，用于缓存优化）
- **Python依赖**: `redis==5.0.1`

#### 快速安装
```bash
# Windows (使用Chocolatey)
choco install redis-64

# Linux (Ubuntu/Debian)
sudo apt install redis-server

# macOS
brew install redis
```

#### 配置文件设置
```yaml
redis:
  host: "localhost"
  port: 6379
  db: 0
  password: null
  
  pool_config:
    max_connections: 20
    retry_on_timeout: true
    health_check_interval: 30
```

## ⚡ 性能优化

### 缓存策略
- **双重缓存**: 内存 + Redis
- **智能TTL**: 根据数据类型动态调整
- **自动清理**: 过期缓存自动清理

### 性能监控
```python
from utils.performance_monitor import performance_monitor

@performance_monitor(slow_threshold=1.0)
def your_function():
    # 你的代码
    pass
```

### 连接池管理
- MySQL连接池自动管理
- Redis连接池优化
- 健康检查和自动重连

## 🛡️ 安全特性

### 文件安全
- 路径遍历攻击防护
- 恶意文件检测
- MIME类型验证
- 文件大小限制

### 访问控制
- 用户会话管理
- 操作日志记录
- 安全事件监控

## 🔧 部署和配置

### 环境变量
```bash
export ENV=development
export REDIS_HOST=localhost
export ENABLE_PERFORMANCE_MONITORING=true
```

### 健康检查
```bash
# 系统状态
curl http://localhost:8888/api/health

# 缓存状态
curl http://localhost:8888/api/cache/status
```

### 日志管理
```bash
# 查看应用日志
python scripts/log_manager.py

# 维护日志
python scripts/maintain_logs.py
```

## 🚨 故障排除

### 常见问题

#### MySQL连接失败
```bash
# 检查服务状态
sudo systemctl status mysql

# 检查端口
netstat -tlnp | grep 3306
```

#### Redis连接失败
```bash
# 测试连接
redis-cli ping

# 检查端口
netstat -an | grep 6379
```

#### 性能问题
- 启用性能监控
- 检查缓存命中率
- 优化数据库查询

## 📊 监控端点

| 端点 | 描述 |
|------|------|
| `/api/health` | 系统健康检查 |
| `/api/status` | 系统状态信息 |
| `/api/cache/status` | 缓存状态 |
| `/api/performance` | 性能指标 |

## 📚 相关资源

- [项目主页](README.md)
- [MySQL官方文档](https://dev.mysql.com/doc/)
- [Redis官方文档](https://redis.io/documentation)

---

**版本**: 2.0.0 | **更新**: 2025年1月
