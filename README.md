# 🗂️ 文件管理系统

<div align="center">
  <h3>基于 Flask 的现代化文件管理系统</h3>
  <p>安全 • 高效 • 易用 • 功能丰富</p>
  
  [![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
  [![Flask Version](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
</div>

## 🌟 核心特性

### 📁 文件管理
- **智能浏览**: 树形结构，支持分页和实时搜索
- **多文件上传**: 拖拽上传，进度显示，类型验证
- **安全下载**: 防盗链保护，断点续传
- **批量操作**: 选择、删除、移动、复制
- **实时预览**: 图片、文本、代码文件预览

### ✏️ 在线编辑
- **代码编辑器**: 基于 CodeMirror 6，支持 50+ 种语言
- **语法高亮**: 智能语法检测和高亮显示
- **搜索替换**: 正则表达式支持，批量替换
- **多主题**: 默认、Monokai、Eclipse、Dracula 等
- **智能功能**: 自动补全、括号匹配、代码折叠

### 🔒 安全保护
- **访问控制**: 基于角色的权限管理
- **文件验证**: 类型、大小、路径安全检查
- **速率限制**: API 调用频率控制
- **安全上传**: 恶意文件检测和隔离
- **日志审计**: 完整的操作日志记录

### 📊 系统监控
- **实时状态**: 磁盘使用、内存状态、CPU 负载
- **性能指标**: 响应时间、吞吐量统计
- **智能告警**: 资源阈值监控和通知
- **日志分析**: 结构化日志，多格式支持

## 📸 界面预览

### 文件管理器
- 🗂️ 现代化的文件列表界面
- 📱 响应式设计，支持移动端
- 🎨 直观的操作按钮和图标

### 在线编辑器
- 💻 专业的代码编辑环境
- 🌈 多主题支持，护眼模式
- ⚡ 实时语法检查和高亮

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.7 或更高版本
- **操作系统**: Windows、macOS、Linux
- **浏览器**: Chrome、Firefox、Safari、Edge
- **磁盘空间**: 建议 100MB 以上

### ⚡ 一键启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd file_manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python main.py

# 4. 访问系统
# 打开浏览器访问: http://localhost:8888
```

### 🔧 自定义配置
```bash
# 复制配置模板
cp env.example .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

## 🏗️ 架构设计

```
file_manager/
├── 📁 core/                   # 核心模块
│   ├── app.py                # Flask 应用工厂
│   └── config.py             # 配置管理
├── 📁 api/routes/             # API 路由层
│   ├── file_ops.py           # 文件操作 API
│   ├── upload.py             # 上传服务 API
│   ├── download.py           # 下载服务 API
│   ├── system.py             # 系统监控 API
│   └── editor.py             # 编辑器 API
├── 📁 services/               # 业务服务层
│   ├── file_service.py       # 文件操作服务
│   ├── editor_service.py     # 编辑器服务
│   ├── security_service.py   # 安全验证服务
│   └── system_service.py     # 系统监控服务
├── 📁 utils/                  # 工具模块
│   ├── logger.py             # 日志系统
│   └── file_utils.py         # 文件工具
├── 📁 static/                 # 前端资源
│   ├── css/                  # 样式文件
│   ├── js/                   # JavaScript
│   └── images/               # 图片资源
├── 📁 templates/              # 页面模板
│   ├── index.html            # 文件管理主页
│   └── editor.html           # 在线编辑器
├── 📁 docs/                   # 项目文档
├── 📁 logs/                   # 日志文件
├── main.py                   # 程序入口
└── requirements.txt          # 依赖清单
```

## ⚙️ 配置指南

<details>
<summary>📋 环境变量配置 (点击展开)</summary>

创建 `.env` 文件并配置以下选项：

```bash
# === 服务器配置 ===
SERVER_HOST=0.0.0.0                    # 监听地址
SERVER_PORT=8888                       # 监听端口
DEBUG_MODE=false                       # 调试模式

# === 安全配置 ===
SECRET_KEY=your-secret-key-here         # 会话密钥
ENABLE_UPLOAD=true                      # 允许上传
ENABLE_DOWNLOAD=true                    # 允许下载
ENABLE_DELETE=true                      # 允许删除

# === 文件限制 ===
MAX_CONTENT_LENGTH=53687091200          # 最大上传大小 (50GB)
MAX_FILE_SIZE=104857600                 # 单文件大小限制 (100MB)
FORBIDDEN_EXTENSIONS=.exe,.bat,.cmd     # 禁止的文件类型

# === 日志配置 ===
LOG_LEVEL=INFO                          # 日志级别
LOG_FORMAT=json                         # 日志格式
LOG_FILE=logs/file_manager.log          # 日志文件
```

</details>

<details>
<summary>🎨 界面配置 (点击展开)</summary>

```bash
# === 主题设置 ===
THEME_COLOR=#4a6fa5                     # 主题颜色
SECONDARY_COLOR=#6c8ebf                 # 次要颜色
APP_NAME=文件管理系统                    # 应用名称

# === 功能开关 ===
ENABLE_DRAG_DROP=true                   # 拖拽上传
ENABLE_PREVIEW=true                     # 文件预览
SHOW_HIDDEN=false                       # 显示隐藏文件
```

</details>

## ⚙️ 配置说明

### 环境变量配置
通过`.env`文件或环境变量配置：

```bash
# 基本配置
ENV=production
ROOT_DIR=/path/to/your/files
APP_NAME=文件管理系统

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8888
DEBUG_MODE=false

# 安全配置
SECRET_KEY=your-secret-key-here
ENABLE_DOWNLOAD=true
ENABLE_UPLOAD=true
ENABLE_DELETE=true

# 文件限制
MAX_CONTENT_LENGTH=53687091200
MAX_FILE_SIZE=104857600
ALLOWED_EXTENSIONS=.txt,.pdf,.doc,.docx,.jpg,.png

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=file_manager.log
```

### 配置文件选项
`config.py`中的主要配置项：

```python
class Config:
    # 根目录配置
    ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
    
    # 文件大小限制
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024 * 1024))
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))
    
    # 安全配置
    FORBIDDEN_EXTENSIONS = {'.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar'}
    
    # 速率限制
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per minute')
    
    # 权限控制
    ENABLE_DOWNLOAD = os.getenv('ENABLE_DOWNLOAD', 'true').lower() == 'true'
    ENABLE_UPLOAD = os.getenv('ENABLE_UPLOAD', 'true').lower() == 'true'
    ENABLE_DELETE = os.getenv('ENABLE_DELETE', 'true').lower() == 'true'
```

## 🔧 核心功能

### 文件管理
- 📁 **文件浏览**: 树形结构，支持分页和搜索
- 📤 **文件上传**: 拖拽上传，多文件支持，类型验证
- 📥 **文件下载**: 安全下载，进度显示
- 🗑️ **文件删除**: 批量删除，回收站支持
- ✏️ **重命名**: 智能重命名，冲突检测
- 📋 **复制移动**: 文件/文件夹复制和移动
- 💻 **在线编辑**: 支持多种编程语言，语法高亮，搜索替换，点击文件名直接进入编辑器

### 安全特性
- 🔒 **文件类型验证**: 白名单和黑名单机制
- 🛡️ **路径安全检查**: 防止路径遍历攻击
- ⚡ **速率限制**: API调用频率限制
- 🔐 **权限控制**: 细粒度功能权限管理
- 🚫 **危险文件过滤**: 自动过滤可执行文件

### 系统监控
- 💾 **磁盘使用**: 实时磁盘空间监控
- 🧠 **内存状态**: 系统内存使用情况
- 📊 **性能统计**: 文件操作性能指标
- 📝 **日志记录**: 完整的操作日志

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python test_app.py

# 使用unittest
python -m unittest test_app.py

# 测试特定模块
python -m unittest test_app.TestFileUtils
```

### 测试覆盖
- ✅ 文件工具函数测试
- ✅ 安全验证测试
- ✅ 路径操作测试
- ✅ 时间格式化测试
- ✅ 集成功能测试

## 📚 API 参考

<details>
<summary>📁 文件管理 API (点击展开)</summary>

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/list` | GET | 获取文件列表 | `path` - 目录路径 |
| `/api/upload` | POST | 上传文件 | `files` - 文件, `path` - 目标目录 |
| `/api/download` | GET | 下载文件 | `path` - 文件路径 |
| `/api/delete` | POST | 删除文件/目录 | `path` - 文件路径 |
| `/api/create_folder` | POST | 创建文件夹 | `path` - 父目录, `name` - 文件夹名 |
| `/api/rename` | POST | 重命名 | `path` - 原路径, `new_name` - 新名称 |
| `/api/copy` | POST | 复制/移动 | `source` - 源路径, `target` - 目标路径 |
| `/api/info` | GET | 系统信息 | 无 |

### 示例请求

```bash
# 获取文件列表
curl "http://localhost:8888/api/list?path=/documents"

# 上传文件
curl -X POST -F "files=@file.txt" -F "path=/uploads" \
     "http://localhost:8888/api/upload"

# 下载文件
curl "http://localhost:8888/api/download?path=/file.txt" -o file.txt
```

</details>

<details>
<summary>✏️ 编辑器 API (点击展开)</summary>

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/editor/open` | POST | 打开文件编辑 | `path` - 文件路径 |
| `/api/editor/save` | POST | 保存文件 | `path` - 文件路径, `content` - 内容 |
| `/api/editor/preview` | GET | 文件预览 | `path` - 文件路径, `max_lines` - 最大行数 |
| `/api/editor/search` | POST | 文件搜索 | `path`, `search_term`, `case_sensitive` |
| `/api/editor/check-editability` | GET | 检查可编辑性 | `path` - 文件路径 |

### 示例请求

```bash
# 打开文件编辑
curl -X POST -H "Content-Type: application/json" \
     -d '{"path": "/code/main.py"}' \
     "http://localhost:8888/api/editor/open"

# 保存文件
curl -X POST -H "Content-Type: application/json" \
     -d '{"path": "/code/main.py", "content": "print(\"Hello\")"}' \
     "http://localhost:8888/api/editor/save"
```

</details>

## 🚀 部署指南

<details>
<summary>🐳 Docker 部署 (推荐)</summary>

```dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8888

# 启动命令
CMD ["python", "main.py"]
```

```bash
# 构建镜像
docker build -t file-manager .

# 运行容器
docker run -d -p 8888:8888 \
  -v /your/files:/app/files \
  -v /your/logs:/app/logs \
  --name file-manager \
  file-manager
```

</details>

<details>
<summary>⚡ 生产环境部署</summary>

### 使用 Gunicorn (推荐)
```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn -c gunicorn.conf.py main:app
```

### Gunicorn 配置 (gunicorn.conf.py)
```python
# 服务器配置
bind = "0.0.0.0:8888"
workers = 4
worker_class = "sync"
worker_connections = 1000

# 日志配置
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"

# 进程配置
preload_app = True
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件直接服务
    location /static/ {
        alias /path/to/file_manager/static/;
        expires 30d;
    }
}
```

</details>

<details>
<summary>🔧 环境配置</summary>

### 生产环境变量
```bash
# 基础配置
ENV=production
DEBUG_MODE=false
SECRET_KEY=your-super-secret-key-here

# 安全配置
SERVER_HOST=127.0.0.1
SERVER_PORT=8888
RATE_LIMIT=200 per minute

# 日志配置
LOG_LEVEL=WARNING
LOG_FILE=logs/production.log
LOG_BACKUP_COUNT=90
```

### SSL/HTTPS 配置
```bash
# 使用 SSL 证书
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

</details>

## 🔧 开发指南

### 代码风格
- 遵循PEP 8编码规范
- 使用类型提示（Python 3.7+）
- 完整的文档字符串
- 单元测试覆盖

### 添加新功能
1. 在`utils.py`中添加工具函数
2. 在`app.py`中添加API端点
3. 在`test_app.py`中添加测试
4. 更新文档

### 错误处理
- 使用统一的错误响应格式
- 详细的错误日志记录
- 用户友好的错误消息

## 🛠️ 故障排除

<details>
<summary>❓ 常见问题 FAQ (点击展开)</summary>

### 🚫 启动问题

**Q: 端口已被占用**
```bash
# 问题: Address already in use
# 解决方案:
1. 修改 .env 文件中的 SERVER_PORT
2. 或者杀死占用端口的进程：
   sudo lsof -i :8888  # 查看占用进程
   sudo kill -9 <PID>  # 杀死进程
```

**Q: 依赖模块缺失**
```bash
# 问题: ModuleNotFoundError
# 解决方案:
pip install -r requirements.txt
# 或者使用虚拟环境:
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 📁 文件操作问题

**Q: 上传大文件失败**
```bash
# 检查配置项:
MAX_CONTENT_LENGTH=53687091200  # 总上传大小限制
MAX_FILE_SIZE=104857600         # 单文件大小限制
# 确保服务器磁盘空间充足
```

**Q: 文件权限被拒绝**
```bash
# Linux/macOS 权限问题:
chmod 755 /path/to/files
chown -R user:group /path/to/files

# Windows 权限问题:
# 右键 -> 属性 -> 安全 -> 编辑权限
```

**Q: 某些文件类型无法编辑**
```bash
# 检查支持的文件类型:
ALLOWED_EXTENSIONS=.py,.js,.html,.css,.md
FORBIDDEN_EXTENSIONS=.exe,.bat,.cmd

# 或查看编辑器支持列表
```

### 🔧 配置问题

**Q: 环境变量不生效**
```bash
# 确保 .env 文件位置正确 (项目根目录)
# 重新启动应用
# 检查环境变量语法 (无空格)
```

**Q: 日志文件不生成**
```bash
# 检查日志目录权限
mkdir -p logs
chmod 755 logs
# 检查日志配置
LOG_FILE=logs/file_manager.log
LOG_LEVEL=INFO
```

</details>

<details>
<summary>🔍 调试技巧 (点击展开)</summary>

### 启用调试模式
```bash
# 在 .env 文件中设置:
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# 或者临时启用:
DEBUG_MODE=true python main.py
```

### 查看日志
```bash
# 实时查看日志
tail -f logs/file_manager.log

# 搜索错误
grep -i error logs/file_manager.log

# 查看最近的日志
tail -100 logs/file_manager.log
```

### 网络问题排查
```bash
# 检查端口监听
netstat -tlnp | grep 8888

# 测试API连接
curl http://localhost:8888/api/info

# 检查防火墙设置
sudo ufw status  # Ubuntu
```

</details>

## 📈 性能优化

### 已实现的优化
- 文件操作异步处理
- 静态资源压缩
- 数据库连接池
- 缓存机制

### 建议的优化
- 使用Redis缓存
- 文件分片上传
- CDN加速
- 负载均衡

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是Bug报告、功能建议还是代码贡献。

<details>
<summary>📝 如何贡献 (点击展开)</summary>

### 🐛 报告Bug
1. 在 [Issues](../../issues) 中搜索是否已有相关问题
2. 如果没有，创建新的Issue，包含：
   - 详细的问题描述
   - 复现步骤
   - 预期结果和实际结果
   - 系统环境信息

### 💡 功能建议
1. 在 [Issues](../../issues) 中提交功能请求
2. 详细描述功能需求和使用场景
3. 如果可能，提供设计方案或示例

### 🔧 代码贡献
1. **Fork** 本项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 进行开发并测试
4. 提交代码: `git commit -m 'feat: add amazing feature'`
5. 推送分支: `git push origin feature/amazing-feature`
6. 提交 **Pull Request**

### 📋 代码规范
- 遵循 [PEP 8](https://pep8.org/) Python 代码规范
- 添加必要的注释和文档字符串
- 编写单元测试
- 保持代码简洁和可读性

### 🧪 测试要求
```bash
# 运行所有测试
python -m pytest tests/

# 检查代码质量
flake8 .
black --check .
```

</details>

## 📚 文档导航

| 文档 | 描述 |
|------|------|
| [📖 编辑器使用指南](docs/EDITOR_README.md) | 在线编辑器功能详解 |
| [🚀 快速启动指南](docs/STARTUP_GUIDE.md) | 系统启动和验证 |
| [📊 功能特性总结](docs/FEATURE_SUMMARY.md) | 完整功能列表 |
| [🔍 日志系统指南](docs/LOGGING_GUIDE.md) | 日志配置和管理 |

## 📊 项目统计

![GitHub stars](https://img.shields.io/github/stars/username/file-manager?style=social)
![GitHub forks](https://img.shields.io/github/forks/username/file-manager?style=social)
![GitHub issues](https://img.shields.io/github/issues/username/file-manager)
![GitHub license](https://img.shields.io/github/license/username/file-manager)

## 🙏 致谢

感谢以下开源项目和社区：

- **[Flask](https://flask.palletsprojects.com/)** - 优秀的 Python Web 框架
- **[CodeMirror](https://codemirror.net/)** - 强大的代码编辑器组件
- **[Font Awesome](https://fontawesome.com/)** - 丰富的图标库
- **[Bootstrap](https://getbootstrap.com/)** - 响应式前端框架

特别感谢所有的贡献者和用户的支持！

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议发布。

```
MIT License

Copyright (c) 2024 File Manager Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

<div align="center">
  <h3>🌟 如果觉得项目有用，请给个 Star 支持一下！</h3>
  <p>
    <a href="../../stargazers">⭐ Star</a> •
    <a href="../../issues">🐛 Report Bug</a> •
    <a href="../../issues">💡 Request Feature</a>
  </p>
  
  **版本**: v2.0.0 | **更新**: 2024年 | **维护**: 文件管理系统团队
</div>