# 日志系统使用指南

## 概述

文件管理系统现在使用了一个功能强大的结构化日志系统，支持多种日志格式、自动轮转、彩色输出和JSON格式日志。

## 特性

### 🎨 多格式支持
- **JSON格式**: 结构化日志，便于机器解析和分析
- **传统格式**: 人类可读的文本格式
- **彩色输出**: 开发环境下的彩色日志，提高可读性

### 📁 自动轮转
- **时间轮转**: 按天自动轮转日志文件
- **大小限制**: 防止单个日志文件过大
- **自动压缩**: 旧日志文件自动压缩节省空间
- **保留策略**: 可配置保留天数

### 🔍 结构化日志
- **上下文信息**: 记录操作类型、文件路径、用户ID等
- **性能监控**: 记录函数执行时间
- **请求追踪**: 记录HTTP请求信息
- **错误详情**: 完整的异常堆栈信息

### 🌍 多环境支持
- **开发环境**: 彩色控制台输出 + 文件日志
- **生产环境**: 纯文件日志，JSON格式
- **测试环境**: 简化日志输出

## 配置

### 环境变量配置

在 `.env` 文件中配置日志相关选项：

```bash
# 基础日志配置
LOG_LEVEL=INFO                    # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                   # 日志格式: json, standard, detailed
LOG_FILE=logs/file_manager.log    # 日志文件路径
LOG_MAX_SIZE=10485760            # 单个日志文件最大大小 (10MB)
LOG_BACKUP_COUNT=30              # 保留的日志文件数量

# 高级日志配置
LOG_ENABLE_CONSOLE=true           # 是否启用控制台输出
LOG_ENABLE_FILE=true              # 是否启用文件输出
LOG_ENABLE_JSON=true              # 是否启用JSON格式
LOG_ENABLE_COLOR=true             # 是否启用彩色输出
LOG_ROTATION_WHEN=midnight        # 轮转时间: midnight, hour, day
LOG_ROTATION_INTERVAL=1           # 轮转间隔
LOG_COMPRESS_OLD=true             # 是否压缩旧日志文件
```

### 不同环境的默认配置

#### 开发环境 (development)
- 日志级别: DEBUG
- 输出: 控制台 + 文件
- 格式: 彩色 + JSON
- 保留: 7天

#### 生产环境 (production)
- 日志级别: WARNING
- 输出: 仅文件
- 格式: JSON
- 保留: 90天

#### 测试环境 (test)
- 日志级别: WARNING
- 输出: 仅控制台
- 格式: 简化文本

## 使用方法

### 1. 基本日志记录

```python
from utils.logger import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 2. 结构化日志

```python
# 记录带上下文的日志
logger.info(
    "文件上传成功",
    operation="file_upload",
    file_path="/path/to/file.txt",
    file_size=1024,
    user_id="user123",
    duration_ms=150.5
)

# 记录异常
try:
    # 某些操作
    pass
except Exception as e:
    logger.exception(
        "操作失败",
        operation="file_operation",
        error=str(e),
        file_path="/path/to/file"
    )
```

### 3. 装饰器使用

```python
from utils.logger import log_function_call, log_request_info

# 函数调用日志
@log_function_call
def process_file(file_path):
    # 函数逻辑
    pass

# 请求信息日志
@log_request_info
def handle_upload():
    # 处理上传
    pass
```

### 4. 日志级别控制

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# 根据条件记录日志
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"详细调试信息: {expensive_operation()}")

# 动态设置日志级别
logger.setLevel(logging.DEBUG)
```

## 日志管理工具

### 命令行工具

项目提供了 `scripts/log_manager.py` 脚本用于日志管理：

```bash
# 列出所有日志文件
python scripts/log_manager.py list

# 查看日志文件内容
python scripts/log_manager.py view file_manager.log -n 100

# 实时监控日志
python scripts/log_manager.py view file_manager.log -f

# 搜索日志内容
python scripts/log_manager.py search "error"

# 分析日志文件
python scripts/log_manager.py analyze file_manager.log --hours 24

# 清理旧日志文件
python scripts/log_manager.py clean --days 30 --execute
```

### 日志文件结构

```
logs/
├── file_manager.log          # 主日志文件
├── error.log                # 错误日志
├── access.log               # 访问日志
├── archive/                 # 归档目录
│   ├── file_manager.log.2024-01-01
│   └── file_manager.log.2024-01-02
└── backup/                  # 备份目录
```

## 最佳实践

### 1. 日志级别使用

- **DEBUG**: 详细的调试信息，仅在开发时使用
- **INFO**: 一般信息，记录重要的业务操作
- **WARNING**: 警告信息，可能的问题但不影响功能
- **ERROR**: 错误信息，功能无法正常工作
- **CRITICAL**: 严重错误，系统可能崩溃

### 2. 日志内容

- 记录操作类型和结果
- 包含必要的上下文信息
- 避免记录敏感信息（密码、密钥等）
- 使用结构化数据便于分析

### 3. 性能考虑

- 避免在日志中执行昂贵的操作
- 使用条件日志记录
- 合理设置日志级别
- 定期清理旧日志文件

### 4. 监控和分析

- 使用JSON格式便于日志分析工具处理
- 设置日志轮转防止磁盘空间不足
- 监控错误日志数量和频率
- 定期分析日志发现潜在问题

## 故障排除

### 常见问题

1. **日志文件不创建**
   - 检查日志目录权限
   - 确认LOG_FILE路径配置正确

2. **日志级别不生效**
   - 检查LOG_LEVEL环境变量
   - 确认日志记录器名称正确

3. **日志文件过大**
   - 调整LOG_MAX_SIZE配置
   - 检查LOG_BACKUP_COUNT设置
   - 使用日志管理工具清理旧文件

4. **性能问题**
   - 降低日志级别
   - 减少DEBUG日志输出
   - 使用条件日志记录

### 调试技巧

```python
# 临时提高日志级别
import logging
logging.getLogger('file_manager').setLevel(logging.DEBUG)

# 查看日志配置
from utils.logger import get_logger
logger = get_logger(__name__)
print(f"Logger level: {logger.logger.level}")
print(f"Logger handlers: {logger.logger.handlers}")
```

## 扩展和自定义

### 自定义格式化器

```python
from utils.logger import ColoredFormatter

class CustomFormatter(ColoredFormatter):
    def format(self, record):
        # 自定义格式化逻辑
        record.custom_field = "自定义值"
        return super().format(record)
```

### 自定义处理器

```python
import logging.handlers

class CustomHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        # 自定义初始化逻辑
```

### 集成外部日志系统

```python
# 发送日志到外部系统
import requests

class ExternalLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        requests.post('https://logs.example.com/api/logs', json=log_entry)
```

## 总结

新的日志系统提供了强大的功能和灵活的配置选项，能够满足不同环境的需求。通过合理使用结构化日志、自动轮转和日志管理工具，可以大大提高系统的可维护性和问题排查效率。

记住：
- 选择合适的日志级别
- 记录有意义的上下文信息
- 定期维护和清理日志文件
- 利用日志管理工具提高效率
