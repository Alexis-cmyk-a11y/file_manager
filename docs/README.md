# 📚 文件管理系统文档中心

<div align="center">
  <h3>系统文档和使用指南</h3>
  <p>快速找到您需要的所有信息</p>
</div>

## 🎯 快速导航

### 🚀 新用户入门
- **[项目主页](../README.md)** - 项目概述、特性介绍和快速开始

### ⚡ 核心功能
- **在线编辑器** - 基于CodeMirror的专业代码编辑器
- **Markdown预览** - 实时预览功能，支持所有基本语法
- **文件管理** - 完整的文件浏览、上传、下载、删除功能
- **系统监控** - 磁盘使用、内存状态、性能统计

### 🔧 开发者资源
- **项目结构** - 清晰的模块化设计
- **API接口** - RESTful API设计
- **安全特性** - 文件验证、权限控制、速率限制

## 📁 项目结构

```
file_manager/
├── 📁 core/                   # 核心模块
├── 📁 api/routes/             # API路由层
├── 📁 services/               # 业务服务层
├── 📁 utils/                  # 工具模块
├── 📁 static/                 # 前端资源
├── 📁 templates/              # 页面模板
├── 📁 docs/                   # 项目文档
├── 📁 demo_files/             # 示例文件
├── main.py                    # 程序入口
└── requirements.txt           # 依赖清单
```

## 🚀 快速开始

### 环境要求
- **Python**: 3.7 或更高版本
- **操作系统**: Windows、macOS、Linux
- **浏览器**: Chrome、Firefox、Safari、Edge

### 一键启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python main.py

# 3. 访问系统
# 打开浏览器访问: http://localhost:8888
```

## 🎉 核心特性

### ✨ 文件管理
- **智能浏览**: 树形结构，支持分页和实时搜索
- **多文件上传**: 拖拽上传，进度显示，类型验证
- **安全下载**: 防盗链保护，断点续传
- **批量操作**: 选择、删除、移动、复制

### ✨ 在线编辑
- **代码编辑器**: 基于 CodeMirror，支持 50+ 种语言
- **语法高亮**: 智能语法检测和高亮显示
- **搜索替换**: 正则表达式支持，批量替换
- **Markdown预览**: 实时预览，支持所有基本语法
- **多主题**: 默认、Monokai、Eclipse、Dracula 等

### ✨ 安全保护
- **访问控制**: 基于角色的权限管理
- **文件验证**: 类型、大小、路径安全检查
- **速率限制**: API 调用频率控制
- **安全上传**: 恶意文件检测和隔离

## 🔧 配置说明

### 环境变量配置
创建 `.env` 文件并配置以下选项：

```bash
# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8888
DEBUG_MODE=false

# 安全配置
SECRET_KEY=your-secret-key-here
ENABLE_UPLOAD=true
ENABLE_DOWNLOAD=true
ENABLE_DELETE=true

# 文件限制
MAX_CONTENT_LENGTH=53687091200
MAX_FILE_SIZE=104857600
FORBIDDEN_EXTENSIONS=.exe,.bat,.cmd
```

## 🧪 测试状态

- ✅ 文件管理功能: 100% 通过
- ✅ 在线编辑功能: 100% 通过
- ✅ Markdown预览功能: 100% 通过
- ✅ 系统监控功能: 100% 通过
- ✅ 安全验证功能: 100% 通过

## 🚀 部署指南

### Docker 部署 (推荐)
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

### 生产环境部署
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn -c gunicorn.conf.py main:app
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是Bug报告、功能建议还是代码贡献。

### 如何贡献
1. **Fork** 本项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 进行开发并测试
4. 提交代码: `git commit -m 'feat: add amazing feature'`
5. 推送分支: `git push origin feature/amazing-feature`
6. 提交 **Pull Request**

### 代码规范
- 遵循 [PEP 8](https://pep8.org/) Python 代码规范
- 使用类型提示（Python 3.7+）
- 添加必要的注释和文档字符串
- 编写单元测试

## 📞 联系我们

如果您有任何问题或建议，可以通过以下方式联系我们：

- 🐛 问题反馈: [Issues](../../issues)
- 💡 功能建议: [Issues](../../issues)

## 📄 许可证

本项目基于 MIT License 开源协议发布。

---

**🎊 项目状态: 健康运行 | 版本: v2.0.0 | 最后更新: 2024年8月**

*Markdown预览功能已完全实现并通过所有测试，项目处于稳定运行状态。*