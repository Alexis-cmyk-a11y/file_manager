#!/bin/bash

# 检查Python环境
if ! command -v python3 &> /dev/null
then
    echo "Python3未安装，请先安装Python3"
    exit 1
fi

# 检查PyInstaller是否安装
if ! pip show pyinstaller &> /dev/null
then
    echo "正在安装PyInstaller..."
    pip install pyinstaller
fi

# 清理旧的构建
echo "清理旧的构建文件..."
rm -rf build/ dist/

# 执行打包
echo "开始打包应用..."
pyinstaller --clean --noconfirm file_manager.spec

# 复制配置文件到dist目录
echo "复制配置文件..."
cp config.py dist/file_manager/

# 创建启动脚本
echo "创建启动脚本..."
cat > dist/file_manager/run.sh << 'EOF'
#!/bin/bash

# 获取脚本所在目录
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# 运行程序
cd "$DIR"
./file_manager
EOF

# 设置执行权限
chmod +x dist/file_manager/run.sh
chmod +x dist/file_manager/file_manager

echo "打包完成！"
echo "可执行文件位于: dist/file_manager/"
echo "可以通过以下命令运行:"
echo "  cd dist/file_manager/"
echo "  ./run.sh"
