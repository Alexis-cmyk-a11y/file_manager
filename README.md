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
- **🔒 安全保护**: 文件验证、速率限制、恶意文件检测、日志审计
- **⚡ 性能优化**: Redis缓存、本地化资源、连接池管理

## 🚀 快速开始

### 环境要求
- **Python**: 3.7+
- **Redis**: 推荐安装（可选）
- **浏览器**: 现代浏览器

### 安装启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd file_manager

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Redis（可选）
redis-server

# 4. 启动服务
python main.py

# 5. 访问系统
# 浏览器访问: http://localhost:8888
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

## ⚙️ 配置说明

主要配置在 `config.yaml` 文件中，支持环境变量覆盖：

```bash
export ENV=development
export REDIS_HOST=localhost
export ENABLE_PERFORMANCE_MONITORING=true
```

## 📚 相关文档

- [优化总结](docs/OPTIMIZATION_SUMMARY.md) - 项目优化详情
- [Redis设置](docs/REDIS_SETUP.md) - Redis配置和使用

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

### 系统监控
- 健康检查端点 `/api/health`
- 性能监控和统计
- 缓存状态监控
- 系统资源使用

## 📄 许可证

本项目基于 MIT License 开源协议发布。

---

<div align="center">
  <h3>🌟 如果觉得项目有用，请给个 Star 支持一下！</h3>
  
  **版本**: v2.0.0 | **更新**: 2025年
</div>
