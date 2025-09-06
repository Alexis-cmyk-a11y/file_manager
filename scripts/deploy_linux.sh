#!/bin/bash
# Linux部署脚本
# 用于在Linux系统上部署文件管理系统

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "建议不要使用root用户运行此脚本"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统要求
check_system_requirements() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法确定操作系统版本"
        exit 1
    fi
    
    . /etc/os-release
    log_info "操作系统: $PRETTY_NAME"
    
    # 检查Python版本
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python版本: $PYTHON_VERSION"
    
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        log_error "Python版本过低，需要3.8或更高版本"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    log_success "系统要求检查通过"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    . /etc/os-release
    
    case $ID in
        ubuntu|debian)
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-venv python3-dev \
                mysql-client libmysqlclient-dev redis-tools \
                nginx git curl wget
            ;;
        centos|rhel|fedora)
            sudo yum update -y
            sudo yum install -y python3-pip python3-devel \
                mysql-devel redis nginx git curl wget
            ;;
        opensuse*|sles)
            sudo zypper refresh
            sudo zypper install -y python3-pip python3-devel \
                libmysqlclient-devel redis nginx git curl wget
            ;;
        *)
            log_warning "未识别的操作系统，请手动安装依赖"
            ;;
    esac
    
    log_success "系统依赖安装完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    if [[ -d "venv" ]]; then
        log_warning "虚拟环境已存在，是否重新创建？"
        read -p "(y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            log_info "使用现有虚拟环境"
            return
        fi
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    log_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    log_info "安装Python依赖..."
    
    source venv/bin/activate
    pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
}

# 创建目录结构
create_directory_structure() {
    log_info "创建目录结构..."
    
    # 创建根目录
    sudo mkdir -p /data/file_manager
    sudo mkdir -p /data/file_manager/home/users
    sudo mkdir -p /data/file_manager/home/shared
    sudo mkdir -p /data/file_manager/uploads
    sudo mkdir -p /data/file_manager/temp
    sudo mkdir -p /data/file_manager/downloads
    sudo mkdir -p /data/file_manager/logs
    
    # 设置权限
    sudo chmod 755 /data/file_manager
    sudo chmod 755 /data/file_manager/home
    sudo chmod 755 /data/file_manager/home/users
    sudo chmod 755 /data/file_manager/home/shared
    sudo chmod 755 /data/file_manager/uploads
    sudo chmod 777 /data/file_manager/temp
    sudo chmod 755 /data/file_manager/downloads
    sudo chmod 755 /data/file_manager/logs
    
    # 设置所有者
    sudo chown -R $USER:$USER /data/file_manager
    
    log_success "目录结构创建完成"
}

# 配置数据库
configure_database() {
    log_info "配置数据库..."
    
    # 检查MySQL是否运行
    if ! systemctl is-active --quiet mysql && ! systemctl is-active --quiet mysqld; then
        log_warning "MySQL服务未运行，请先启动MySQL服务"
        log_info "启动MySQL服务: sudo systemctl start mysql"
        read -p "MySQL服务启动后按Enter继续..."
    fi
    
    # 运行数据库初始化脚本
    source venv/bin/activate
    python scripts/init_database.py
    
    log_success "数据库配置完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."
    
    # 检查Nginx是否安装
    if ! command -v nginx &> /dev/null; then
        log_warning "Nginx未安装，跳过Nginx配置"
        return
    fi
    
    # 备份原配置
    if [[ -f /etc/nginx/nginx.conf ]]; then
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # 复制Nginx配置
    sudo cp nginx.conf /etc/nginx/sites-available/file-manager
    sudo ln -sf /etc/nginx/sites-available/file-manager /etc/nginx/sites-enabled/
    
    # 更新配置中的路径
    sudo sed -i "s|/path/to/your/file_manager|$(pwd)|g" /etc/nginx/sites-available/file-manager
    
    # 测试Nginx配置
    sudo nginx -t
    
    log_success "Nginx配置完成"
}

# 创建systemd服务
create_systemd_service() {
    log_info "创建systemd服务..."
    
    SERVICE_FILE="/etc/systemd/system/file-manager.service"
    PROJECT_DIR=$(pwd)
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=File Manager System
After=network.target mysql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
ExecStart=$PROJECT_DIR/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    log_success "systemd服务创建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动文件管理器服务
    sudo systemctl enable file-manager
    sudo systemctl start file-manager
    
    # 启动Nginx（如果配置了）
    if [[ -f /etc/nginx/sites-enabled/file-manager ]]; then
        sudo systemctl enable nginx
        sudo systemctl restart nginx
    fi
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 检查服务状态
    if systemctl is-active --quiet file-manager; then
        log_success "文件管理器服务运行正常"
    else
        log_error "文件管理器服务未运行"
        sudo systemctl status file-manager
    fi
    
    # 检查端口
    if netstat -tlnp | grep -q ":8888"; then
        log_success "应用监听端口8888"
    else
        log_warning "应用未监听端口8888"
    fi
    
    # 测试HTTP连接
    if curl -s http://localhost:8888/health > /dev/null; then
        log_success "HTTP连接测试通过"
    else
        log_warning "HTTP连接测试失败"
    fi
    
    log_success "部署验证完成"
}

# 显示部署信息
show_deployment_info() {
    log_info "部署信息:"
    echo "=================================="
    echo "项目目录: $(pwd)"
    echo "数据目录: /data/file_manager"
    echo "虚拟环境: $(pwd)/venv"
    echo "服务名称: file-manager"
    echo "监听端口: 8888"
    echo "=================================="
    echo
    echo "管理命令:"
    echo "  启动服务: sudo systemctl start file-manager"
    echo "  停止服务: sudo systemctl stop file-manager"
    echo "  重启服务: sudo systemctl restart file-manager"
    echo "  查看状态: sudo systemctl status file-manager"
    echo "  查看日志: sudo journalctl -u file-manager -f"
    echo
    echo "访问地址:"
    echo "  本地访问: http://localhost:8888"
    echo "  外部访问: http://$(hostname -I | awk '{print $1}'):8888"
    echo
    echo "默认管理员账户:"
    echo "  邮箱: admin@system.local"
    echo "  密码: admin123"
    echo "  (首次登录后请立即修改密码)"
}

# 主函数
main() {
    echo "=================================="
    echo "文件管理系统 Linux 部署脚本"
    echo "=================================="
    echo
    
    # 检查参数
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        echo "用法: $0 [选项]"
        echo "选项:"
        echo "  --help, -h     显示帮助信息"
        echo "  --skip-deps    跳过系统依赖安装"
        echo "  --skip-nginx   跳过Nginx配置"
        echo "  --skip-service 跳过systemd服务创建"
        exit 0
    fi
    
    # 检查root权限
    check_root
    
    # 检查系统要求
    check_system_requirements
    
    # 安装系统依赖
    if [[ "$1" != "--skip-deps" ]]; then
        install_system_dependencies
    fi
    
    # 创建虚拟环境
    create_virtual_environment
    
    # 安装Python依赖
    install_python_dependencies
    
    # 创建目录结构
    create_directory_structure
    
    # 配置数据库
    configure_database
    
    # 配置Nginx
    if [[ "$1" != "--skip-nginx" ]]; then
        configure_nginx
    fi
    
    # 创建systemd服务
    if [[ "$1" != "--skip-service" ]]; then
        create_systemd_service
    fi
    
    # 启动服务
    start_services
    
    # 验证部署
    verify_deployment
    
    # 显示部署信息
    show_deployment_info
    
    log_success "部署完成！"
}

# 运行主函数
main "$@"
