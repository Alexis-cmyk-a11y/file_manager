# 📁 文件管理系统

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Flask](https://img.shields.io/badge/flask-3.0.0-red.svg)

**一个功能强大、安全可靠的企业级文件管理系统**

*基于目录隔离与硬链接共享技术，提供完整的文件管理解决方案*

[🚀 快速开始](#-快速开始) • [📖 使用指南](#-使用指南) • [🔧 配置说明](#-配置说明) • [📚 API文档](#-api接口)

</div>

## ✨ 核心特性

### 🔐 安全与权限
- **🔒 用户隔离**: 每个用户拥有独立的文件空间，确保数据安全
- **🛡️ 权限控制**: 细粒度的文件访问权限管理
- **🔑 身份认证**: 完整的用户注册、登录、密码管理流程
- **📊 操作审计**: 详细的操作日志记录和审计追踪

### 📁 文件管理
- **📂 完整操作**: 上传、下载、重命名、删除、移动、复制文件
- **🔗 智能共享**: 基于硬链接的零拷贝文件共享机制
- **📝 在线编辑**: 内置CodeMirror编辑器，支持50+种编程语言
- **🌐 拖拽上传**: 现代化的拖拽文件上传体验

### ⚡ 性能与扩展
- **🚀 高性能**: Redis缓存 + MySQL数据库的混合存储架构
- **📈 监控系统**: 实时性能监控和资源使用统计
- **🔄 配置热重载**: 支持配置修改无需重启服务
- **📱 响应式设计**: 完美适配桌面和移动设备

## 🛠️ 技术架构

### 后端技术栈
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 核心开发语言 |
| **Flask** | 3.0.0 | Web框架 |
| **MySQL** | 5.7+ | 关系型数据库 |
| **Redis** | 5.0+ | 缓存和会话存储 |
| **SQLAlchemy** | 2.0+ | ORM框架 |
| **bcrypt** | 4.1+ | 密码加密 |

### 前端技术栈
| 技术 | 用途 |
|------|------|
| **HTML5/CSS3** | 现代化界面设计 |
| **JavaScript ES6+** | 交互逻辑实现 |
| **CodeMirror** | 代码编辑器 |
| **FontAwesome** | 图标库 |

### 系统特性
- **🔧 配置管理**: YAML配置文件，支持多环境
- **📊 日志系统**: 结构化日志，自动轮转
- **🛡️ 安全防护**: 路径验证、文件类型检查
- **⚡ 性能优化**: 连接池、缓存策略

## 🚀 快速开始

### 📋 系统要求

| 组件 | 最低版本 | 推荐版本 |
|------|----------|----------|
| **Python** | 3.8 | 3.11+ |
| **MySQL** | 5.7 | 8.0+ |
| **Redis** | 5.0 | 7.0+ |
| **内存** | 512MB | 2GB+ |
| **磁盘** | 1GB | 10GB+ |

### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/your-username/file_manager.git
cd file_manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
cp config/development.yaml config/local.yaml
# 编辑 config/local.yaml 配置数据库连接

# 4. 初始化数据库
python scripts/init_database.py

# 5. 启动应用
python main.py
```

### 🌐 访问地址

启动成功后，您可以通过以下地址访问系统：

| 功能 | 地址 | 说明 |
|------|------|------|
| **🏠 主页** | `http://localhost:8888` | 系统首页和文件浏览 |
| **📝 在线编辑** | `http://localhost:8888/editor` | 代码编辑器 |
| **🔐 用户登录** | `http://localhost:8888/login` | 用户认证 |
| **📊 系统监控** | `http://localhost:8888/system` | 系统状态监控 |

### 👤 默认账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| **管理员** | `admin@system.local` | `Asdasd123` | 系统管理员账户 |

## 📖 使用指南

### 🎯 核心功能

#### 📁 文件管理
- **📤 文件上传**: 支持单文件/批量上传，拖拽上传
- **📥 文件下载**: 单文件下载，批量打包下载
- **✏️ 文件操作**: 重命名、删除、移动、复制
- **🔍 文件搜索**: 按名称、类型、大小搜索
- **📊 文件预览**: 图片、文本、代码文件预览

#### 🔗 文件共享
- **🤝 智能共享**: 基于硬链接的零拷贝共享
- **🔒 权限控制**: 只读权限，保护原始文件
- **📱 共享管理**: 查看、搜索、清理共享文件
- **🔄 自动同步**: 原文件修改自动反映到共享区

#### 📝 在线编辑
- **💻 代码编辑**: 支持50+种编程语言语法高亮
- **⌨️ 快捷键**: 完整的编辑器快捷键支持
- **💾 自动保存**: 可配置的自动保存功能
- **🔍 搜索替换**: 强大的搜索和替换功能

#### 🔐 用户认证
- **👤 用户注册**: 邮箱验证码注册
- **🔑 安全登录**: 密码加密存储
- **🔄 密码管理**: 修改密码、重置密码
- **📊 会话管理**: 安全的会话控制

### 🎨 界面特性
- **📱 响应式设计**: 完美适配各种设备
- **🌙 主题支持**: 可配置的界面主题
- **⚡ 快速操作**: 右键菜单、快捷键支持
- **📊 实时反馈**: 操作状态实时显示

## 🔌 API接口

### 🔐 认证接口

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/auth/login` | POST | 用户登录 | `username`, `password` |
| `/api/auth/register` | POST | 用户注册 | `username`, `email`, `password`, `code` |
| `/api/auth/change-password` | POST | 修改密码 | `old_password`, `new_password` |
| `/api/auth/reset-password` | POST | 重置密码 | `email`, `code`, `new_password` |
| `/api/auth/logout` | POST | 用户登出 | - |

### 📁 文件管理接口

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/files/list` | GET | 获取文件列表 | `path`, `page`, `size` |
| `/api/files/upload` | POST | 上传文件 | `file`, `path` |
| `/api/files/download` | GET | 下载文件 | `path` |
| `/api/files/rename` | PUT | 重命名文件 | `old_path`, `new_name` |
| `/api/files/delete` | DELETE | 删除文件 | `path` |
| `/api/files/move` | PUT | 移动文件 | `old_path`, `new_path` |
| `/api/files/copy` | POST | 复制文件 | `old_path`, `new_path` |

### 🤝 文件共享接口

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/sharing/share` | POST | 共享文件 | `path` |
| `/api/sharing/unshare` | DELETE | 取消共享 | `path` |
| `/api/sharing/list` | GET | 获取共享列表 | `page`, `size` |
| `/api/sharing/download` | GET | 下载共享文件 | `share_id` |

### 📊 系统监控接口

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/api/system/info` | GET | 系统信息 | - |
| `/api/system/stats` | GET | 系统统计 | - |
| `/api/system/logs` | GET | 系统日志 | `level`, `page`, `size` |

## 🗂️ 项目结构

```
file_manager/
├── 📁 api/                     # API路由层
│   └── routes/                 # 具体路由实现
│       ├── auth.py            # 认证相关接口
│       ├── file_ops.py        # 文件操作接口
│       ├── sharing.py         # 文件共享接口
│       └── system.py          # 系统监控接口
├── 📁 core/                    # 应用核心
│   ├── app.py                 # Flask应用工厂
│   ├── config.py              # 配置基类
│   └── config_manager.py      # 配置管理器
├── 📁 services/                # 业务服务层
│   ├── auth_service.py        # 认证服务
│   ├── file_service.py        # 文件服务
│   ├── mysql_service.py       # 数据库服务
│   └── redis_service.py       # 缓存服务
├── 📁 templates/               # HTML模板
│   ├── index.html             # 主页
│   ├── login.html             # 登录页
│   └── editor.html            # 编辑器页
├── 📁 static/                  # 静态资源
│   ├── css/                   # 样式文件
│   ├── js/                    # JavaScript文件
│   └── fonts/                 # 字体文件
├── 📁 config/                  # 配置文件
│   ├── config.yaml            # 主配置文件
│   ├── development.yaml       # 开发环境配置
│   └── production.yaml        # 生产环境配置
├── 📁 scripts/                 # 管理脚本
│   ├── init_database.py       # 数据库初始化
│   ├── manage_config.py       # 配置管理
│   └── log_manager.py         # 日志管理
├── 📁 utils/                   # 工具函数
│   ├── auth_middleware.py     # 认证中间件
│   ├── file_utils.py          # 文件工具
│   └── logger.py              # 日志工具
├── 📁 home/                    # 用户数据目录
│   ├── users/                 # 用户文件目录
│   └── shared/                # 共享文件目录
└── 📁 docs/                    # 文档目录
    └── CONFIGURATION.md       # 配置文档
```

## ⚙️ 配置说明

### 🔧 多环境配置

系统支持多环境配置管理，通过 `config/environment.txt` 文件控制当前运行环境：

```bash
# 开发环境
echo "development" > config/environment.txt

# 生产环境  
echo "production" > config/environment.txt
```

### 📝 配置文件结构

| 文件 | 用途 | 说明 |
|------|------|------|
| `config.yaml` | 主配置文件 | 基础配置和默认值 |
| `development.yaml` | 开发环境 | 开发调试配置 |
| `production.yaml` | 生产环境 | 生产部署配置 |
| `environment.txt` | 环境选择 | 当前运行环境标识 |

### 🔑 关键配置项

#### 服务器配置
```yaml
server:
  host: "0.0.0.0"        # 监听地址
  port: 8888             # 监听端口
  workers: 1             # 工作进程数
  timeout: 30            # 请求超时时间
```

#### 数据库配置
```yaml
database:
  mysql:
    host: "localhost"    # MySQL主机
    port: 3306           # MySQL端口
    database: "file_manager"  # 数据库名
    username: "root"     # 用户名
    password: "password" # 密码
  redis:
    host: "localhost"    # Redis主机
    port: 6379           # Redis端口
```

#### 安全配置
```yaml
security:
  secret_key: "your-secret-key"  # 应用密钥
  session_timeout: 3600          # 会话超时时间
  max_login_attempts: 5          # 最大登录尝试次数
```

### 🛠️ 配置管理工具

```bash
# 验证配置文件
python scripts/validate_config.py

# 查看配置信息
python scripts/manage_config.py info

# 备份配置
python scripts/manage_config.py backup

# 恢复配置
python scripts/manage_config.py restore
```

> 📖 **详细配置说明**: 请参考 [配置文档](docs/CONFIGURATION.md)

## 🚀 部署指南

### 🐳 Docker部署

```bash
# 构建镜像
docker build -t file-manager .

# 运行容器
docker run -d \
  --name file-manager \
  -p 8888:8888 \
  -v /path/to/data:/app/home \
  -e MYSQL_HOST=your-mysql-host \
  -e REDIS_HOST=your-redis-host \
  file-manager
```

### ☁️ 云服务器部署

#### 腾讯云部署
```bash
# 使用腾讯云配置
cp config/tencent_cloud.template.py config/tencent_cloud.py
# 编辑腾讯云配置

# 启动服务
python main.py
```

### 🔧 生产环境优化

```yaml
# production.yaml
debug: false
log_level: WARNING
server:
  workers: 4
  timeout: 60
cache:
  enabled: true
  default_ttl: 3600
security:
  file_validation:
    check_file_content: true
```

## 🛠️ 开发指南

### 📋 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 启动开发服务器
python main.py

# 运行测试
pytest tests/

# 代码格式化
black .
flake8 .
```

### 🔍 调试工具

- **日志查看**: `tail -f logs/file_manager.log`
- **配置验证**: `python scripts/validate_config.py`
- **数据库管理**: `python scripts/init_database.py`
- **性能监控**: 访问 `/system` 页面

### 📊 监控指标

| 指标 | 说明 | 正常范围 |
|------|------|----------|
| **响应时间** | API平均响应时间 | < 200ms |
| **内存使用** | 应用内存占用 | < 512MB |
| **磁盘使用** | 用户文件占用 | 根据需求 |
| **并发连接** | 同时在线用户 | < 100 |

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题
- 使用 [GitHub Issues](https://github.com/your-username/file_manager/issues) 报告Bug
- 提供详细的错误信息和复现步骤

### 💡 功能建议
- 通过 [GitHub Discussions](https://github.com/your-username/file_manager/discussions) 提出新功能建议
- 描述使用场景和预期效果

### 🔧 代码贡献
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 支持与帮助

### 📚 文档资源
- [配置文档](docs/CONFIGURATION.md) - 详细配置说明
- [API文档](#-api接口) - 完整API接口文档
- [常见问题](docs/FAQ.md) - 常见问题解答

### 🆘 获取帮助
- **GitHub Issues**: 技术问题和Bug报告
- **GitHub Discussions**: 功能讨论和社区交流
- **Email**: support@filemanager.com

### 🏆 致谢
感谢所有为这个项目做出贡献的开发者和用户！

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

[![GitHub stars](https://img.shields.io/github/stars/your-username/file_manager.svg?style=social&label=Star)](https://github.com/your-username/file_manager)
[![GitHub forks](https://img.shields.io/github/forks/your-username/file_manager.svg?style=social&label=Fork)](https://github.com/your-username/file_manager/fork)

*让文件管理变得简单高效* 🚀

</div>

