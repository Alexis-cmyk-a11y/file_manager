#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装网络文件下载功能的依赖
"""

import subprocess
import sys
import os

def install_requirements():
    """安装requirements.txt中的依赖"""
    print("📦 安装网络文件下载功能依赖...")
    
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        requirements_file = os.path.join(project_root, 'requirements.txt')
        
        if not os.path.exists(requirements_file):
            print("❌ requirements.txt文件不存在")
            return False
        
        print(f"📁 项目根目录: {project_root}")
        print(f"📋 依赖文件: {requirements_file}")
        
        # 安装依赖
        print("\n🔧 正在安装依赖...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖安装成功!")
            print(result.stdout)
            return True
        else:
            print("❌ 依赖安装失败!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 安装过程中发生错误: {e}")
        return False

def check_download_directory():
    """检查并创建download目录"""
    print("\n📁 检查download目录...")
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(project_root, 'download')
        
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
            print(f"✅ 创建download目录: {download_dir}")
        else:
            print(f"✅ download目录已存在: {download_dir}")
        
        # 检查目录权限
        if os.access(download_dir, os.W_OK):
            print("✅ download目录可写")
        else:
            print("⚠️  download目录不可写，请检查权限")
            
        return True
        
    except Exception as e:
        print(f"❌ 创建download目录失败: {e}")
        return False

def test_imports():
    """测试关键模块导入"""
    print("\n🧪 测试模块导入...")
    
    try:
        import requests
        print("✅ requests模块导入成功")
        
        import urllib.parse
        print("✅ urllib.parse模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 网络文件下载功能安装脚本")
    print("=" * 50)
    
    # 安装依赖
    if not install_requirements():
        print("\n❌ 依赖安装失败，请检查错误信息")
        return False
    
    # 检查download目录
    if not check_download_directory():
        print("\n❌ download目录创建失败")
        return False
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 网络文件下载功能安装完成!")
    print("\n📋 下一步:")
    print("1. 启动Flask应用: python main.py")
    print("2. 访问首页: http://localhost:5000")
    print("3. 点击'网络下载'按钮测试功能")
    print("4. 运行测试脚本: python test_web_download.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
