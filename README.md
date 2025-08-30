# 文件管理系统

一个轻量、实用的文件管理系统。以目录隔离与硬链接共享为核心，提供上传/下载、在线编辑与简洁的共享能力。

## 🚀 项目背景

文件管理系统是一个基于Python Flask的现代化Web应用，专为解决团队文件共享和管理需求而设计。系统采用硬链接技术实现零拷贝文件共享，确保存储效率的同时提供完整的文件管理功能。

## ✨ 主要特性

- **🔒 目录隔离**: 每个用户拥有独立的 `home/users/<username>` 工作区，确保数据安全
- **🔗 硬链接共享**: 将文件共享到 `home/shared/<username>_shared`，只读、零拷贝、节省存储空间
- **📝 在线编辑**: 内置代码编辑器，支持语法高亮，常用文本/代码直接在线编辑
- **📁 基础操作**: 完整的文件浏览、上传、下载、重命名、删除、移动功能
- **🛡️ 安全防护**: 路径校验、类型检查、操作日志、权限控制
- **🌐 现代化UI**: 响应式设计，支持拖拽上传，美观易用的用户界面
- **⚙️ 多环境配置**: 支持开发、生产环境配置，灵活部署

## 🛠️ 技术栈

- **后端**: Python 3.8+, Flask, SQLAlchemy
- **前端**: HTML5, CSS3, JavaScript (ES6+), CodeMirror
- **数据库**: MySQL, Redis
- **存储**: 本地文件系统 + 硬链接
- **部署**: 支持Docker容器化部署

## 📦 安装说明

### 系统要求

- Python 3.8 或更高版本
- MySQL 5.7+ 或 MariaDB 10.2+
- Redis 5.0+
- 支持硬链接的文件系统（NTFS、ext4等）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/file_manager.git
cd file_manager
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境

复制并编辑配置文件：
```bash
cp config/development.yaml config/local.yaml
# 编辑 config/local.yaml 和 config/environment.txt
```

### 4. 初始化数据库

```bash
python scripts/init_database.py
```

### 5. 启动应用

```bash
python main.py
```

## 🚀 快速开始

### 开发环境启动

```bash
# 设置环境为开发模式
echo "development" > config/environment.txt

# 启动应用
python main.py
```

### 生产环境部署

```bash
# 设置环境为生产模式
echo "production" > config/environment.txt

# 使用生产配置启动
python main.py
```

### 访问地址

- **主页**: `http://localhost:8888`
- **文件管理**: `http://localhost:8888/files`
- **在线编辑器**: `http://localhost:8888/editor`
- **共享文件**: `http://localhost:8888/shared`
- **用户管理**: `http://localhost:8888/admin`

## 📚 使用指南

### 文件管理

1. **上传文件**: 拖拽文件到上传区域或点击选择文件
2. **创建文件夹**: 点击"新建文件夹"按钮
3. **文件操作**: 右键文件/文件夹进行复制、移动、删除等操作
4. **批量操作**: 选择多个文件进行批量处理

### 文件共享

1. **选择文件**: 在文件列表中选择要共享的文件
2. **设置权限**: 选择共享权限（只读/读写）
3. **生成链接**: 系统自动生成共享链接
4. **分享链接**: 将链接发送给需要访问的用户

### 在线编辑

1. **打开文件**: 点击文件或使用编辑器页面
2. **编辑内容**: 在CodeMirror编辑器中修改文件
3. **保存更改**: 按Ctrl+S或点击保存按钮
4. **版本控制**: 系统自动记录文件修改历史

## 🔌 API 文档

### 认证接口

```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/logout
GET  /api/auth/profile
```

### 文件管理接口

```http
GET    /api/files/list          # 获取文件列表
POST   /api/files/upload        # 上传文件
GET    /api/files/download      # 下载文件
PUT    /api/files/rename        # 重命名文件
DELETE /api/files/delete        # 删除文件
POST   /api/files/move          # 移动文件
POST   /api/files/copy          # 复制文件
```

### 共享接口

```http
POST   /api/sharing/share       # 创建共享
DELETE /api/sharing/unshare     # 取消共享
GET    /api/sharing/shared      # 获取共享列表
GET    /api/sharing/access      # 访问共享文件
```

### 编辑器接口

```http
GET    /api/editor/open         # 打开文件编辑
POST   /api/editor/save         # 保存文件
GET    /api/editor/history      # 获取编辑历史
```

## 🗂️ 目录结构详解

```
file_manager/
├── api/                    # 后端API路由
│   ├── routes/            # 具体路由实现
│   │   ├── auth.py        # 认证相关API
│   │   ├── file_ops.py    # 文件操作API
│   │   ├── upload.py      # 文件上传API
│   │   ├── download.py    # 文件下载API
│   │   ├── editor.py      # 编辑器API
│   │   └── sharing.py     # 文件共享API
│   └── __init__.py        # API模块初始化
├── core/                   # 应用核心
│   ├── app.py             # Flask应用实例
│   ├── config.py          # 配置基类
│   └── config_manager.py  # 配置管理器
├── services/               # 业务服务层
│   ├── auth_service.py    # 认证服务
│   ├── file_service.py    # 文件服务
│   ├── upload_service.py  # 上传服务
│   ├── download_service.py # 下载服务
│   ├── editor_service.py  # 编辑器服务
│   ├── sharing_service.py # 共享服务
│   └── mysql_service.py   # 数据库服务
├── templates/              # HTML模板
│   ├── index.html         # 主页模板
│   ├── editor.html        # 编辑器模板
│   ├── login.html         # 登录页面
│   └── shared_files.html  # 共享文件页面
├── static/                 # 静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件
│   └── fonts/             # 字体文件
├── config/                 # 配置文件
│   ├── config.yaml        # 主配置文件
│   ├── development.yaml   # 开发环境配置
│   ├── production.yaml    # 生产环境配置
│   └── environment.txt    # 环境标识文件
├── scripts/                # 管理脚本
│   ├── init_database.py   # 数据库初始化
│   ├── setup_auth.py      # 认证设置
│   └── manage_config.py   # 配置管理
├── utils/                  # 工具函数
│   ├── auth_middleware.py # 认证中间件
│   ├── file_utils.py      # 文件工具
│   └── logger.py          # 日志工具
└── home/                   # 用户数据目录
    ├── users/              # 用户个人目录
    └── shared/             # 共享文件目录
```

## 🔧 配置说明

系统支持多环境配置，详细配置说明请参考 [配置文档](docs/CONFIGURATION.md)。

### 关键配置项

- **服务器配置**: 主机地址、端口、工作进程数
- **数据库配置**: MySQL连接参数、Redis配置
- **安全配置**: 密钥、会话超时、速率限制
- **存储配置**: 文件上传限制、存储路径

## 🚀 部署指南

### Docker 部署

```bash
# 构建镜像
docker build -t file-manager .

# 运行容器
docker run -d -p 8888:8888 \
  -v /path/to/data:/app/home \
  -v /path/to/config:/app/config \
  file-manager
```

### 传统部署

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境
cp config/production.yaml config/local.yaml
# 编辑配置文件

# 启动应用
python main.py
```

### 反向代理配置

Nginx配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 测试

### 运行测试

```bash
# 单元测试
python -m pytest tests/

# 集成测试
python -m pytest tests/integration/

# 覆盖率测试
python -m pytest --cov=app tests/
```

### 性能测试

```bash
# 使用ab进行压力测试
ab -n 1000 -c 10 http://localhost:8888/

# 使用wrk进行负载测试
wrk -t12 -c400 -d30s http://localhost:8888/
```

## 📊 监控与日志

### 日志配置

- 应用日志: `logs/file_manager.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

### 性能监控

- 请求响应时间
- 文件操作性能
- 数据库查询性能
- 系统资源使用情况

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/your-username/file_manager.git

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行代码检查
flake8 .
black .
isort .
```

## 📝 更新日志

### v2.0.0 (2025-01-XX)
- ✨ 全新的现代化UI设计
- 🔒 增强的安全特性
- 📱 响应式设计支持
- 🚀 性能优化

### v1.5.0 (2024-12-XX)
- 🔗 硬链接共享功能
- 📝 在线代码编辑器
- 🛡️ 权限控制系统

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

## 📞 联系我们

- **项目主页**: https://github.com/your-username/file_manager
- **问题反馈**: https://github.com/your-username/file_manager/issues
- **邮箱**: support@filemanager.local

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

