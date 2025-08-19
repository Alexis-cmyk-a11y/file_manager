# 文件管理系统

## 项目概述
这是一个基于Flask的文件管理系统，提供文件上传、下载和管理功能。

## 功能特点
- 文件上传与下载
- 文件列表浏览
- 权限管理
- 日志记录

## 环境要求
- Python 3.7+
- Windows/Linux/macOS
- 推荐使用虚拟环境

## 安装指南
1. 克隆项目：
   ```bash
   git clone [项目地址]
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 配置说明
配置文件`config.py`包含以下主要设置：

### 基本配置
```python
# 根目录配置（使用当前目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# 上传文件大小限制（50GB）
MAX_CONTENT_LENGTH = 50 * 1024 * 1024 * 1024

# 允许上传的文件类型（空表示允许所有类型）
ALLOWED_EXTENSIONS = set()
```

### 服务器配置
```python
SERVER_HOST = '0.0.0.0'  # 监听地址
SERVER_PORT = 8888       # 监听端口
DEBUG_MODE = True        # 调试模式开关
TEMPLATES_AUTO_RELOAD = True  # 模板自动重载
```

### 权限控制
```python
# 功能开关
ENABLE_DOWNLOAD = True    # 是否允许下载文件
ENABLE_DELETE = True     # 是否允许删除文件/文件夹
ENABLE_UPLOAD = True     # 是否允许上传文件
ENABLE_CREATE_FOLDER = True  # 是否允许创建文件夹
ENABLE_RENAME = True     # 是否允许重命名
ENABLE_MOVE_COPY = True  # 是否允许移动/复制

# 细粒度权限控制
PERMISSIONS = {
    'upload': True,      # 上传权限
    'download': True,    # 下载权限
    'delete': True,      # 删除权限
    'rename': True,      # 重命名权限
    'create_folder': True, # 创建文件夹权限
    'admin_ops': False   # 管理员操作权限
}
```

### 日志配置
```python
LOG_LEVEL = 'INFO'  # 可选：DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'file_manager.log'
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
```

### 界面配置
```python
APP_NAME = "文件管理系统"
THEME_COLOR = "#4a6fa5"  # 主题颜色
SECONDARY_COLOR = "#6c8ebf"  # 次要颜色

# 前端配置
FRONTEND_CONFIG = {
    'app_name': '文件管理系统',
    'default_view': 'list',  # 默认视图(list/grid)
    'page_size': 20,         # 每页显示文件数
    'show_hidden': False     # 是否显示隐藏文件
}
```

### 环境配置
```python
ENV = 'development'  # 当前环境(development/production)
if ENV == 'production':
    DEBUG_MODE = False
    TEMPLATES_AUTO_RELOAD = False
    STATIC_COMPRESS = True
```

## 打包指南
使用PyInstaller打包为可执行文件：

1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 生成spec文件：

   **Windows系统**:
   ```bash
   pyinstaller --name=file_manager --onefile --add-data "templates;templates" --add-data "static;static" app.py
   ```

   **Linux/macOS系统**:
   ```bash
   pyinstaller --name=file_manager --onefile --add-data 'templates:templates' --add-data 'static:static' app.py
   ```

   注意事项：
   - Windows使用分号(;)作为路径分隔符
   - Linux/macOS使用冒号(:)作为路径分隔符
   - 确保路径相对于app.py的位置正确

3. 修改spec文件（可选）：
   - 添加图标：`icon='icon.ico'`
   - 排除模块：`excludes=['module_name']`

4. 执行打包：
   ```bash
   pyinstaller file_manager.spec
   ```

## API文档

### 文件管理API

#### 1. 获取文件列表
- **URL**: `/api/files`
- **方法**: GET
- **参数**:
  - `path` (可选): 指定目录路径，默认为根目录
- **响应**:
  ```json
  {
    "success": true,
    "files": [
      {
        "name": "file.txt",
        "path": "/file.txt",
        "size": 1024,
        "modified": "2023-01-01T12:00:00",
        "is_dir": false
      }
    ]
  }
  ```

#### 2. 上传文件
- **URL**: `/api/upload`
- **方法**: POST
- **参数**:
  - `file`: 上传的文件内容
  - `path` (可选): 上传目标路径
- **响应**:
  ```json
  {
    "success": true,
    "message": "文件上传成功",
    "path": "/uploaded_file.txt"
  }
  ```

#### 3. 下载文件
- **URL**: `/api/download`
- **方法**: GET
- **参数**:
  - `path`: 要下载的文件路径
- **响应**: 文件内容

#### 4. 删除文件/目录
- **URL**: `/api/delete`
- **方法**: DELETE
- **参数**:
  - `path`: 要删除的文件/目录路径
- **响应**:
  ```json
  {
    "success": true,
    "message": "删除成功"
  }
  ```

#### 5. 创建目录
- **URL**: `/api/create_folder`
- **方法**: POST
- **参数**:
  - `path`: 要创建的目录路径
- **响应**:
  ```json
  {
    "success": true,
    "message": "目录创建成功"
  }
  ```

#### 6. 重命名文件/目录
- **URL**: `/api/rename`
- **方法**: POST
- **参数**:
  - `old_path`: 原路径
  - `new_path`: 新路径
- **响应**:
  ```json
  {
    "success": true,
    "message": "重命名成功"
  }
  ```

#### 7. 复制/移动文件
- **URL**: `/api/move_copy`
- **方法**: POST
- **参数**:
  - `src_path`: 源路径
  - `dst_path`: 目标路径
  - `operation`: "copy"或"move"
- **响应**:
  ```json
  {
    "success": true,
    "message": "操作成功"
  }
  ```

### 错误响应
所有API在出错时返回以下格式的响应：
```json
{
  "success": false,
  "error": {
    "code": "错误代码",
    "message": "错误描述"
  }
}
```

常见错误代码：
- `400`: 无效请求
- `403`: 权限不足
- `404`: 文件不存在
- `500`: 服务器内部错误

## 运行说明
### 开发模式
```bash
python app.py
```

### 生产模式
1. 直接运行可执行文件：
   ```bash
   dist/file_manager
   ```
2. 访问应用：
   ```
   http://localhost:5000
   ```

## 常见问题
### 1. 打包后找不到config.py
- 确保`config.py`与可执行文件在同一目录
- 或使用`--add-data`选项包含配置文件

### 2. 应用立即退出
- 创建批处理文件保持窗口打开：
  ```bat
  @echo off
  cd /d %~dp0
  file_manager.exe
  pause
  ```

### 3. 缺少依赖
- 确保所有依赖已正确打包
- 检查`_internal`目录是否完整

## 项目结构
```
project/
├── app.py            # 主程序
├── config.py         # 配置文件
├── requirements.txt  # 依赖列表
├── README.md         # 说明文档
├── dist/             # 打包输出目录
└── build/            # 打包临时文件
```

## 贡献指南
欢迎贡献代码！请遵循以下步骤：

1. Fork本项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 代码风格
- 遵循PEP 8编码规范
- 为新增功能添加单元测试
- 确保所有测试通过

## 测试说明
项目包含单元测试和集成测试：

### 运行测试
```bash
python -m pytest tests/
```

### 测试覆盖率
```bash
python -m pytest --cov=.
```

## 版本历史
### v1.0.0 (2025-08-19)
- 初始版本发布
- 包含基本文件管理功能

## 截图示例
(请在此处添加系统截图或演示GIF)
