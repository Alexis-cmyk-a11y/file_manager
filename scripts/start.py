#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动脚本
包含配置验证、环境检查、应用启动等功能
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask', 'pyyaml', 'redis', 'pymysql', 'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 依赖包检查通过")
    return True

def check_config_files():
    """检查配置文件"""
    config_dir = Path("config")
    
    if not config_dir.exists():
        print("❌ 配置目录不存在")
        return False
    
    required_files = ["config.yaml", "environment.txt"]
    missing_files = []
    
    for file_name in required_files:
        if not (config_dir / file_name).exists():
            missing_files.append(file_name)
    
    if missing_files:
        print(f"❌ 缺少配置文件: {', '.join(missing_files)}")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def validate_config():
    """验证配置文件"""
    try:
        # 运行配置验证脚本
        result = subprocess.run([
            sys.executable, "scripts/validate_config.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 配置验证通过")
            return True
        else:
            print("❌ 配置验证失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 配置验证脚本执行失败: {e}")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        # 这里可以添加数据库连接测试
        # 暂时跳过，因为需要数据库服务运行
        print("⚠️  数据库连接检查跳过（需要数据库服务运行）")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_ports():
    """检查端口占用"""
    import socket
    
    config_dir = Path("config")
    if not config_dir.exists():
        return False
    
    try:
        # 读取配置文件获取端口
        with open(config_dir / "environment.txt", 'r') as f:
            env = f.read().strip()
        
        env_config_file = config_dir / f"{env}.yaml"
        if env_config_file.exists():
            import yaml
            with open(env_config_file, 'r') as f:
                env_config = yaml.safe_load(f)
                port = env_config.get('server', {}).get('port', 8888)
        else:
            port = 8888
        
        # 检查端口是否被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"❌ 端口 {port} 已被占用")
            return False
        else:
            print(f"✅ 端口 {port} 可用")
            return True
            
    except Exception as e:
        print(f"⚠️  端口检查跳过: {e}")
        return True

def show_startup_info():
    """显示启动信息"""
    print("\n" + "=" * 60)
    print("🚀 文件管理系统启动检查")
    print("=" * 60)
    
    # 显示环境信息
    config_dir = Path("config")
    if config_dir.exists():
        env_file = config_dir / "environment.txt"
        if env_file.exists():
            with open(env_file, 'r') as f:
                env = f.read().strip()
            print(f"🌍 运行环境: {env}")
        
        # 显示配置文件信息
        config_files = list(config_dir.glob("*.yaml")) + list(config_dir.glob("*.txt"))
        print(f"📁 配置文件: {len(config_files)} 个")
    
    print(f"🐍 Python版本: {sys.version.split()[0]}")
    print(f"📂 工作目录: {os.getcwd()}")
    print(f"⏰ 启动时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def run_health_check():
    """运行健康检查"""
    print("\n🔍 运行健康检查...")
    
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("配置文件", check_config_files),
        ("配置验证", validate_config),
        ("端口检查", check_ports),
        ("数据库连接", check_database_connection),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}检查...")
        if check_func():
            passed += 1
        else:
            print(f"❌ {check_name}检查失败")
    
    print(f"\n📊 健康检查结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有检查通过，可以启动应用")
        return True
    else:
        print("❌ 部分检查失败，请解决问题后重试")
        return False

def start_application():
    """启动应用"""
    print("\n🚀 启动应用...")
    
    try:
        # 启动主应用
        result = subprocess.run([
            sys.executable, "main.py"
        ])
        
        if result.returncode == 0:
            print("✅ 应用正常退出")
        else:
            print(f"❌ 应用异常退出，退出码: {result.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️  应用被用户中断")
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")

def main():
    """主函数"""
    # 显示启动信息
    show_startup_info()
    
    # 运行健康检查
    if not run_health_check():
        print("\n❌ 健康检查失败，无法启动应用")
        sys.exit(1)
    
    # 询问是否启动应用
    while True:
        response = input("\n是否启动应用？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            break
        elif response in ['n', 'no', '否']:
            print("👋 应用启动已取消")
            sys.exit(0)
        else:
            print("请输入 y 或 n")
    
    # 启动应用
    start_application()

if __name__ == '__main__':
    main()
