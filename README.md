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
配置文件`config.py`应包含以下设置：
```python
class Config:
    # 文件操作权限: 'read_only' 或 'read_write'
    FILE_OPERATION_PERMISSION = 'read_write'  
    
    # 服务器设置
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5000
    
    # 日志设置
    LOG_FILE = 'file_manager.log'
    LOG_LEVEL = 'INFO'  # DEBUG/INFO/WARNING/ERROR/CRITICAL
```

## 打包指南
使用PyInstaller打包为可执行文件：

1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 生成spec文件：
   ```bash
   pyinstaller --name=file_manager --onefile --add-data="templates;templates" --add-data="static;static" app.py
   ```

3. 修改spec文件（可选）：
   - 添加图标：`icon='icon.ico'`
   - 排除模块：`excludes=['module_name']`

4. 执行打包：
   ```bash
   pyinstaller file_manager.spec
   ```

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

## 许可证
[MIT License](LICENSE)
