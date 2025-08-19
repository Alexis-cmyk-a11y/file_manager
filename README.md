# 项目构建说明

## 项目简介
这是一个Python应用程序项目，使用PyInstaller打包为可执行文件。

## 构建方法

### Windows系统构建
1. 安装依赖：
   ```bash
   pip install pyinstaller
   ```

2. 生成spec文件：
   ```bash
   pyinstaller --onefile --exclude-module config --specpath . app.py
   ```

3. 修改spec文件：
   - 在Analysis部分添加：
     ```python
     datas=[('static','static'), ('templates','templates')]
     ```

4. 执行打包：
   ```bash
   pyinstaller app.spec
   ```

### Linux系统构建
步骤与Windows相同，但需要在Linux环境下执行。

## 运行说明
1. 将生成的app.exe(Windows)或app(Linux)与config.py放在同一目录
2. 运行程序：
   ```bash
   ./app  # Linux
   app.exe  # Windows
   ```

## 注意事项
1. config.py需要单独提供，不会被包含在可执行文件中
2. 静态资源文件(static和templates)会被打包进可执行文件
3. 如需修改资源文件，需要重新打包
