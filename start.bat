@echo off
chcp 65001 >nul
title 文件管理系统启动器

echo.
echo ========================================
echo           文件管理系统 v2.0
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 📦 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 💡 未找到虚拟环境，将使用系统Python
)

:: 检查依赖
echo 🔍 检查依赖包...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📥 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

:: 启动应用
echo.
echo 🚀 启动文件管理系统...
echo.
python start.py

:: 如果直接启动失败，尝试启动主应用
if errorlevel 1 (
    echo.
    echo 💡 尝试直接启动主应用...
    python app.py
)

echo.
echo 👋 应用已退出
pause
