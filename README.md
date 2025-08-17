# 文件管理器 - Linux打包指南

## 系统要求
- Linux操作系统
- Python 3.6+
- pip (Python包管理工具)

## 构建步骤

1. 确保已安装Python3和pip
2. 克隆或下载本项目代码
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 运行构建脚本：
   ```bash
   chmod +x build_linux.sh
   ./build_linux.sh
   ```

## 运行程序

构建完成后，可执行文件位于`dist/file_manager/`目录下：

```bash
cd dist/file_manager/
./run.sh
```

## 配置说明

程序使用外部的`config.py`文件进行配置。构建完成后，该文件会被复制到`dist/file_manager/`目录下。

您可以编辑该文件来修改程序配置，修改后无需重新构建。

## 文件结构

- `app.py`: 主程序入口
- `config.py`: 配置文件
- `static/`: 静态资源文件
- `templates/`: 模板文件
- `file_manager.spec`: PyInstaller打包配置
- `build_linux.sh`: 构建脚本

## 注意事项

1. 首次运行构建脚本可能需要安装PyInstaller
2. 确保构建环境与运行环境兼容
3. 配置文件修改后需要重启程序生效
