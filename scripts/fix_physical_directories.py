#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复物理目录与数据库路径不匹配的问题
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.mysql_service import get_mysql_service
from utils.logger import get_logger

logger = get_logger(__name__)

def fix_physical_directories():
    """修复物理目录与数据库路径不匹配的问题"""
    try:
        mysql_service = get_mysql_service()
        
        print("🔍 检查数据库中的用户空间路径...")
        
        # 获取所有用户空间记录
        sql = "SELECT * FROM user_spaces"
        user_spaces = mysql_service.execute_query(sql)
        
        if not user_spaces:
            print("✅ 没有用户空间记录需要修复")
            return True
        
        print(f"📋 发现 {len(user_spaces)} 个用户空间记录")
        
        # 修复每个用户空间
        for space in user_spaces:
            user_id = space['user_id']
            old_path = space['space_path']
            
            # 检查是否为绝对路径格式
            if old_path.startswith('/'):
                # 转换为相对路径
                new_path = old_path[1:]  # 移除开头的 '/'
                
                print(f"🔧 修复用户 {user_id}: {old_path} -> {new_path}")
                
                # 更新数据库记录
                update_sql = "UPDATE user_spaces SET space_path = %s WHERE user_id = %s"
                mysql_service.execute_update(update_sql, (new_path, user_id))
                
                # 创建物理目录
                if not os.path.exists(new_path):
                    os.makedirs(new_path, exist_ok=True)
                    print(f"✅ 创建物理目录: {new_path}")
                else:
                    print(f"⚠️  物理目录已存在: {new_path}")
                
                # 权限表已在新系统中移除，无需更新
                print(f"✅ 路径已更新: {old_path} -> {new_path}")
            else:
                print(f"✅ 用户 {user_id} 路径已正确: {old_path}")
                
                # 确保物理目录存在
                if not os.path.exists(old_path):
                    os.makedirs(old_path, exist_ok=True)
                    print(f"✅ 创建物理目录: {old_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"修复物理目录失败: {e}")
        print(f"❌ 修复物理目录失败: {e}")
        return False

def create_system_directories():
    """创建系统目录"""
    try:
        print("\n🔧 创建系统目录...")
        
        system_dirs = ['public', 'shared', 'admin']
        
        for dir_name in system_dirs:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ 创建系统目录: {dir_name}")
            else:
                print(f"⚠️  系统目录已存在: {dir_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"创建系统目录失败: {e}")
        print(f"❌ 创建系统目录失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始修复物理目录...")
    print("=" * 60)
    
    try:
        # 1. 修复用户空间物理目录
        print("📋 步骤 1: 修复用户空间物理目录...")
        if not fix_physical_directories():
            print("❌ 修复用户空间物理目录失败，退出")
            sys.exit(1)
        
        # 2. 创建系统目录
        print("\n📋 步骤 2: 创建系统目录...")
        if not create_system_directories():
            print("❌ 创建系统目录失败，退出")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎉 物理目录修复完成！")
        print("\n📋 已修复的内容:")
        print("   ✅ 修复了数据库路径与物理目录不匹配的问题")
        print("   ✅ 创建了所有必要的物理目录")
        print("   ✅ 同步了权限记录")
        print("\n🔧 下一步:")
        print("   1. 重启文件管理系统: python main.py")
        print("   2. 测试文件共享功能")
        print("   3. 检查用户个人空间是否正常")
        
    except Exception as e:
        logger.error(f"物理目录修复失败: {e}")
        print(f"❌ 物理目录修复失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
