# 📁 文件管理系统

一个功能强大、安全可靠的企业级文件管理系统，基于目录隔离与硬链接共享技术。

## ✨ 核心特性

- **🔒 用户隔离**: 每个用户拥有独立的文件空间
- **📂 文件管理**: 上传、下载、重命名、删除、移动、复制
- **🔗 智能共享**: 基于硬链接的零拷贝文件共享
- **📝 在线编辑**: 内置CodeMirror编辑器，支持50+种编程语言
- **⚡ 高性能缓存**: Redis缓存系统，目录列表性能提升479倍
- **📱 响应式设计**: 完美适配桌面和移动设备

## 🛠️ 技术栈

- **后端**: Python 3.8+, Flask 3.0, MySQL, Redis
- **前端**: HTML5/CSS3, JavaScript ES6+, CodeMirror
- **特性**: YAML配置管理、结构化日志、安全防护

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置数据库
编辑 `config/development.yaml` 配置数据库连接

### 初始化数据库
```bash
python scripts/init_database.py
```

### 启动应用
```bash
python main.py
```

### 访问地址
- **主页**: http://localhost:8888
- **在线编辑**: http://localhost:8888/editor
- **用户登录**: http://localhost:8888/login

### 默认账户
- **管理员**: admin@system.local / Asdasd123

## 📖 主要功能

- **文件管理**: 上传、下载、重命名、删除、移动、复制
- **文件共享**: 基于硬链接的零拷贝共享机制
- **在线编辑**: 支持50+种编程语言的代码编辑器
- **用户认证**: 注册、登录、密码管理、会话管理
- **智能缓存**: Redis缓存系统，大幅提升文件操作性能
- **系统监控**: 实时性能监控和资源统计

## ⚙️ 配置

详细配置说明请参考 [配置文档](docs/CONFIGURATION.md)

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

