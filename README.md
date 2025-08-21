# 文件管理系统 v2.0

## 🚀 项目概述
这是一个基于Flask的现代化文件管理系统，提供安全、高效、易用的文件管理功能。经过全面优化，支持环境变量配置、增强的安全特性、完整的测试覆盖和更好的用户体验。

## ✨ 新版本特性
- 🔒 **增强安全性**: 文件类型验证、路径安全检查、速率限制
- 🌍 **环境配置**: 支持.env文件和环境变量配置
- 🧪 **完整测试**: 单元测试和集成测试覆盖
- 🛠️ **工具函数**: 丰富的文件操作和安全验证工具
- 📱 **现代界面**: 响应式设计，支持拖拽上传
- 📊 **系统监控**: 磁盘使用情况、内存状态等系统信息
- 🚀 **启动脚本**: 智能启动脚本，自动环境检查

## 🏗️ 项目结构
```
file_manager/
├── app.py                 # 主应用程序
├── config.py              # 配置文件
├── utils.py               # 工具函数库
├── start.py               # 智能启动脚本
├── test_app.py            # 测试文件
├── env.example            # 环境变量示例
├── requirements.txt       # 依赖列表
├── README.md              # 项目文档
├── static/                # 静态资源
│   ├── css/
│   └── js/
└── templates/             # HTML模板
    └── index.html
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.7+
- Windows/Linux/macOS
- 推荐使用虚拟环境

### 2. 安装依赖
```bash
# 克隆项目
git clone [项目地址]
cd file_manager

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境
```bash
# 复制环境配置示例
cp env.example .env

# 编辑配置文件
# 根据需要修改 .env 文件中的配置
```

### 4. 启动应用
```bash
# 方式1: 使用智能启动脚本（推荐）
python start.py

# 方式2: 直接启动
python app.py

# 方式3: 运行测试
python test_app.py
```

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

## 📚 API文档

### 文件操作API

#### 获取文件列表
```http
GET /api/list?path=directory_path
```

#### 上传文件
```http
POST /api/upload
Content-Type: multipart/form-data

files: [file1, file2, ...]
path: target_directory
```

#### 下载文件
```http
GET /api/download?path=file_path
```

#### 删除文件/目录
```http
POST /api/delete
Content-Type: application/json

{
    "path": "file_or_directory_path"
}
```

#### 创建文件夹
```http
POST /api/create_folder
Content-Type: application/json

{
    "path": "parent_directory",
    "name": "folder_name"
}
```

#### 重命名
```http
POST /api/rename
Content-Type: application/json

{
    "path": "old_path",
    "new_name": "new_name"
}
```

#### 复制/移动
```http
POST /api/copy
Content-Type: application/json

{
    "source": "source_path",
    "target": "target_directory"
}
```

#### 系统信息
```http
GET /api/info
```

## 🚀 部署

### 开发环境
```bash
python start.py
# 选择选项1启动应用
```

### 生产环境
```bash
# 设置环境变量
export ENV=production
export DEBUG_MODE=false
export SECRET_KEY=your-production-secret-key

# 启动应用
python app.py
```

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8888

CMD ["python", "app.py"]
```

### 使用Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8888 app:app
```

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

## 🐛 常见问题

### Q: 上传大文件失败
A: 检查`MAX_CONTENT_LENGTH`和`MAX_FILE_SIZE`配置

### Q: 权限被拒绝
A: 检查文件/目录权限和`ENABLE_*`配置

### Q: 端口被占用
A: 修改`SERVER_PORT`配置或停止占用端口的服务

### Q: 文件类型不支持
A: 检查`ALLOWED_EXTENSIONS`和`FORBIDDEN_EXTENSIONS`配置

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

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 🙏 致谢

- Flask框架及其生态系统
- Font Awesome图标库
- 所有贡献者的支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**版本**: v2.0.0  
**最后更新**: 2025年1月  
**维护者**: 文件管理系统团队