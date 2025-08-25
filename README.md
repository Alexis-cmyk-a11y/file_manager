# 🗂️ 文件管理系统

<div align="center">
  <h3>基于 Flask 的现代化文件管理系统</h3>
  <p>安全 • 高效 • 易用 • 功能丰富</p>
  
  [![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
  [![Flask Version](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
</div>

## 🌟 核心特性

- **📁 文件管理**: 智能浏览、多文件上传、安全下载、批量操作、实时预览
- **✏️ 在线编辑**: CodeMirror编辑器，支持50+种编程语言，语法高亮
- **🗄️ 数据存储**: MySQL数据库支持，文件信息持久化、操作日志记录
- **🔒 安全保护**: 文件验证、速率限制、恶意文件检测、日志审计
- **⚡ 性能优化**: Redis缓存、MySQL连接池、本地化资源

## 🚀 快速开始

### 环境要求
- **Python**: 3.7+
- **MySQL**: 5.7+ (推荐8.0+)
- **Redis**: 推荐安装（可选）

### 安装启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd file_manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化MySQL数据库
python scripts/init_database.py

# 4. 启动服务
python main.py

# 5. 访问系统
# 浏览器访问: http://localhost:8888
# 默认管理员: admin@system.local / Asdasd123
```

## 🏗️ 项目结构

```
file_manager/
├── core/           # 核心模块
├── services/       # 业务服务
├── api/routes/     # API路由
├── utils/          # 工具模块
├── static/         # 前端资源
├── templates/      # 页面模板
├── docs/           # 项目文档
├── main.py         # 程序入口
└── config.yaml     # 配置文件
```

## 🔧 主要功能

### 文件管理
- 文件浏览、上传、下载、删除、重命名
- 文件夹创建、复制、移动
- 文件搜索和过滤
- 拖拽上传支持

### 在线编辑
- 支持多种编程语言
- 语法高亮和代码提示
- 多主题支持
- 实时保存

### 用户认证系统
- 用户注册和登录
- 邮箱验证码注册
- 管理员账户管理
- 权限控制和会话管理

## 📚 相关文档

- [部署指南](docs/DEPLOYMENT.md) - 快速部署说明
- [技术指南](docs/TECHNICAL_GUIDE.md) - 完整技术文档

## 📄 许可证

本项目基于 MIT License 开源协议发布。

---

<div align="center">
  <h3>🌟 如果觉得项目有用，请给个 Star 支持一下！</h3>
  
  **版本**: v2.0.0 | **更新**: 2025年
</div>
