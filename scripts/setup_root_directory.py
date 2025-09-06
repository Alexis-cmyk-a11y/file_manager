#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根目录设置脚本
用于创建和配置文件管理系统的根目录
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def create_root_directory():
    """创建根目录结构"""
    try:
        from core.config import config
        
        root_dir = config.FILESYSTEM_ROOT
        print(f"🚀 设置根目录: {root_dir}")
        
        # 创建根目录
        if not os.path.exists(root_dir):
            os.makedirs(root_dir, exist_ok=True)
            print(f"✅ 创建根目录: {root_dir}")
        else:
            print(f"✅ 根目录已存在: {root_dir}")
        
        # 创建子目录结构
        subdirs = [
            'home/users',
            'home/shared',
            'uploads',
            'temp',
            'downloads'
        ]
        
        for subdir in subdirs:
            full_path = os.path.join(root_dir, subdir)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                print(f"✅ 创建子目录: {full_path}")
            else:
                print(f"✅ 子目录已存在: {full_path}")
        
        # 创建示例文件
        sample_files = [
            ('README.txt', '这是文件管理系统的根目录\n\n目录结构:\n- home/users: 用户个人目录\n- home/shared: 共享文件目录\n- uploads: 上传文件目录\n- temp: 临时文件目录\n- downloads: 下载文件目录'),
            ('home/users/README.txt', '用户个人目录\n\n每个用户登录后都会有自己的子目录'),
            ('home/shared/README.txt', '共享文件目录\n\n用户可以在这里共享文件')
        ]
        
        for file_path, content in sample_files:
            full_path = os.path.join(root_dir, file_path)
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 创建示例文件: {full_path}")
        
        print(f"\n🎉 根目录设置完成!")
        print(f"📁 根目录路径: {root_dir}")
        print(f"📋 目录结构:")
        print(f"   ├── home/")
        print(f"   │   ├── users/     (用户个人目录)")
        print(f"   │   └── shared/    (共享文件目录)")
        print(f"   ├── uploads/       (上传文件目录)")
        print(f"   ├── temp/          (临时文件目录)")
        print(f"   ├── downloads/     (下载文件目录)")
        print(f"   └── README.txt     (说明文件)")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建根目录失败: {e}")
        return False

def test_directory_access():
    """测试目录访问权限"""
    try:
        from core.config import config
        
        root_dir = config.FILESYSTEM_ROOT
        print(f"\n🧪 测试目录访问权限...")
        
        # 测试读取权限
        if os.access(root_dir, os.R_OK):
            print(f"✅ 读取权限: 正常")
        else:
            print(f"❌ 读取权限: 失败")
            return False
        
        # 测试写入权限
        test_file = os.path.join(root_dir, 'test_write.tmp')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ 写入权限: 正常")
        except Exception as e:
            print(f"❌ 写入权限: 失败 - {e}")
            return False
        
        # 测试目录创建权限
        test_dir = os.path.join(root_dir, 'test_dir.tmp')
        try:
            os.makedirs(test_dir, exist_ok=True)
            os.rmdir(test_dir)
            print(f"✅ 目录创建权限: 正常")
        except Exception as e:
            print(f"❌ 目录创建权限: 失败 - {e}")
            return False
        
        print(f"🎉 所有权限测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 权限测试失败: {e}")
        return False

def show_config_info():
    """显示配置信息"""
    try:
        from core.config import config
        
        print(f"\n📋 当前配置信息:")
        print(f"   根目录: {config.FILESYSTEM_ROOT}")
        print(f"   应用名称: {config.APP_NAME}")
        print(f"   版本: {config.VERSION}")
        print(f"   环境: {config.ENV}")
        print(f"   调试模式: {config.DEBUG_MODE}")
        
    except Exception as e:
        print(f"❌ 获取配置信息失败: {e}")

def main():
    """主函数"""
    print("🔧 文件管理系统根目录设置工具")
    print("=" * 50)
    
    # 显示配置信息
    show_config_info()
    
    # 创建根目录
    if create_root_directory():
        # 测试权限
        if test_directory_access():
            print(f"\n🎉 根目录设置完成!")
            print(f"📝 下一步:")
            print(f"   1. 启动系统: python main.py")
            print(f"   2. 访问: http://localhost:8888")
            print(f"   3. 使用管理员账户登录")
            print(f"   4. 现在应该能看到配置的根目录内容")
        else:
            print(f"\n❌ 权限测试失败，请检查目录权限")
    else:
        print(f"\n❌ 根目录设置失败")

if __name__ == '__main__':
    main()
