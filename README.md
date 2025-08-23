# 🗂️ 文件管理系统

<div align="center">
  <h3>基于 Flask 的现代化文件管理系统</h3>
  <p>安全 • 高效 • 易用 • 功能丰富</p>
  
  [![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
  [![Flask Version](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
</div>

## 🌟 核心特性

### 📁 文件管理
- **智能浏览**: 树形结构，支持分页和实时搜索
- **多文件上传**: 拖拽上传，进度显示，类型验证
- **安全下载**: 防盗链保护，断点续传
- **批量操作**: 选择、删除、移动、复制
- **实时预览**: 图片、文本、代码文件预览

### ✏️ 在线编辑
- **代码编辑器**: 基于 CodeMirror，支持 50+ 种语言
- **语法高亮**: 智能语法检测和高亮显示
- **搜索替换**: 正则表达式支持，批量替换
- **多主题**: 默认、Monokai、Eclipse、Dracula 等

### 🔒 安全保护
- **文件验证**: 类型、大小、路径安全检查
- **速率限制**: API 调用频率控制
- **安全上传**: 恶意文件检测和隔离
- **日志审计**: 完整的操作日志记录

### ⚡ 性能优化
- **Redis缓存**: 文件信息和目录列表缓存
- **本地化资源**: CDN资源本地缓存，加载速度提升90%+
- **连接池**: 高效的数据库连接管理

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.7 或更高版本
- **Redis**: 推荐安装以获得更好性能
- **浏览器**: 现代浏览器（Chrome、Firefox、Safari、Edge）

### ⚡ 一键启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd file_manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Redis（可选，推荐）
redis-server

# 4. 启动服务
python main.py

# 5. 访问系统
# 打开浏览器访问: http://localhost:8888
```

## 🏗️ 项目结构

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
│   ├── redis_service.py      # Redis服务
│   └── cache_service.py      # 缓存服务
├── 📁 utils/                  # 工具模块
│   ├── logger.py             # 日志系统
│   └── file_utils.py         # 文件工具
├── 📁 static/                 # 前端资源
├── 📁 templates/              # 页面模板
├── 📁 docs/                   # 项目文档
├── main.py                   # 程序入口
└── requirements.txt          # 依赖清单
```

## ⚙️ 配置说明

### 主要配置项
所有配置都在 `core/config.py` 文件中：

```python
class Config:
    # 文件大小限制
    MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  # 1GB
    
    # 禁止的文件类型
    FORBIDDEN_EXTENSIONS = {'.com', '.pif', '.app'}
    
    # Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    
    # 服务器配置
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8888
```

## 🔧 核心功能

### 文件管理
- 📁 **文件浏览**: 树形结构，支持分页和搜索
- 📤 **文件上传**: 拖拽上传，多文件支持，类型验证
- 📥 **文件下载**: 安全下载，进度显示
- ✏️ **重命名**: 智能重命名，冲突检测
- 📋 **复制移动**: 文件/文件夹复制和移动
- 💻 **在线编辑**: 支持多种编程语言，语法高亮

### 安全特性
- 🔒 **文件类型验证**: 防止上传危险文件
- 🛡️ **路径安全检查**: 防止路径遍历攻击
- ⚡ **速率限制**: API调用频率限制
- 📝 **操作日志**: 完整的操作记录

## 📚 API 参考

### 文件管理 API

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/list` | GET | 获取文件列表 | `path` - 目录路径 |
| `/api/upload` | POST | 上传文件 | `files` - 文件, `path` - 目标目录 |
| `/api/download` | GET | 下载文件 | `path` - 文件路径 |
| `/api/delete` | POST | 删除文件/目录 | `path` - 文件路径 |
| `/api/create_folder` | POST | 创建文件夹 | `path` - 父目录, `name` - 文件夹名 |
| `/api/rename` | POST | 重命名 | `path` - 原路径, `new_name` - 新名称 |
| `/api/copy` | POST | 复制 | `source` - 源路径, `target` - 目标路径 |
| `/api/move` | POST | 移动 | `source` - 源路径, `target` - 目标路径 |

### 编辑器 API

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/api/editor/open` | POST | 打开文件编辑 | `path` - 文件路径 |
| `/api/editor/save` | POST | 保存文件 | `path` - 文件路径, `content` - 内容 |

## 🛠️ 故障排除

### 常见问题

**Q: 端口被占用**
```bash
# 修改配置文件中的端口
# core/config.py: SERVER_PORT = 9999
```

**Q: 上传大文件失败**
```bash
# 调整文件大小限制
# core/config.py: MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
```

**Q: Redis连接失败**
```bash
# 检查Redis服务是否启动
redis-cli ping

# 或禁用Redis使用内存缓存
# 应用会自动降级到内存存储
```

## 📈 性能优化

### 已实现的优化
- **⚡ 本地化资源**: 所有CDN资源本地缓存，加载速度提升90%+
- **💾 Redis缓存**: 文件信息和目录列表缓存
- **🗜️ 静态资源压缩**: 减少传输大小
- **🔗 连接池管理**: 高效的Redis连接管理

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. **Fork** 本项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交代码: `git commit -m 'feat: add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 添加必要的注释和文档字符串
- 保持代码简洁和可读性

## 📚 相关文档

- [CDN优化总结](docs/CDN_OPTIMIZATION_SUMMARY.md) - 性能优化详情
- [Redis设置指南](docs/REDIS_SETUP.md) - Redis配置和使用

## 📄 许可证

本项目基于 MIT License 开源协议发布。

---

<div align="center">
  <h3>🌟 如果觉得项目有用，请给个 Star 支持一下！</h3>
  <p>
    <a href="../../stargazers">⭐ Star</a> •
    <a href="../../issues">🐛 Report Bug</a> •
    <a href="../../issues">💡 Request Feature</a>
  </p>
  
  **版本**: v2.0.0 | **更新**: 2025年
</div> 