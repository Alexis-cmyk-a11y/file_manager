#!/bin/bash

# 文件管理系统启动脚本 v2.0
# 适用于Linux和macOS系统

# 设置颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo
    echo "========================================"
    echo "           文件管理系统 v2.0"
    echo "========================================"
    echo
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "未找到Python，请先安装Python 3.7+"
            echo "下载地址: https://www.python.org/downloads/"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # 检查版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "Python版本: $PYTHON_VERSION"
}

# 检查虚拟环境
check_venv() {
    print_info "检查虚拟环境..."
    
    if [ -f "venv/bin/activate" ]; then
        print_info "激活虚拟环境..."
        source venv/bin/activate
        print_success "虚拟环境已激活"
    else
        print_warning "未找到虚拟环境，将使用系统Python"
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖包..."
    
    if ! $PYTHON_CMD -c "import flask" &> /dev/null; then
        print_warning "缺少依赖包，正在安装..."
        $PYTHON_CMD -m pip install -r requirements.txt
        
        if [ $? -ne 0 ]; then
            print_error "依赖安装失败"
            exit 1
        fi
        
        print_success "依赖安装完成"
    else
        print_success "依赖检查通过"
    fi
}

# 启动应用
start_app() {
    print_info "启动文件管理系统..."
    echo
    
    # 尝试使用启动脚本
    if [ -f "start.py" ]; then
        print_info "使用智能启动脚本..."
        $PYTHON_CMD start.py
        
        if [ $? -ne 0 ]; then
            print_warning "启动脚本失败，尝试直接启动主应用..."
            $PYTHON_CMD app.py
        fi
    else
        print_info "直接启动主应用..."
        $PYTHON_CMD app.py
    fi
}

# 主函数
main() {
    print_header
    
    # 检查Python
    check_python
    
    # 检查虚拟环境
    check_venv
    
    # 检查依赖
    check_dependencies
    
    # 启动应用
    start_app
    
    echo
    print_info "应用已退出"
}

# 捕获中断信号
trap 'echo -e "\n${YELLOW}⚠️  应用被用户中断${NC}"; exit 0' INT

# 运行主函数
main "$@"
