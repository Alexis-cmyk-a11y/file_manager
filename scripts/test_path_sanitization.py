#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径清理功能测试脚本
测试修复后的路径清理功能是否正确处理相对路径
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.security_service import get_security_service
from utils.logger import get_logger

logger = get_logger(__name__)

def test_path_sanitization():
    """测试路径清理功能"""
    print("🔍 测试路径清理功能...")
    
    security_service = get_security_service()
    
    # 测试管理员用户的路径处理
    print("\n📋 测试管理员用户路径处理:")
    
    test_cases = [
        {
            'user_id': 1,
            'email': 'admin@system.local',
            'path': 'README.txt',
            'expected_prefix': '/data/file_manager'
        },
        {
            'user_id': 1,
            'email': 'admin@system.local',
            'path': 'downloads/test.txt',
            'expected_prefix': '/data/file_manager'
        },
        {
            'user_id': 1,
            'email': 'admin@system.local',
            'path': '.',
            'expected': '/data/file_manager'
        },
        {
            'user_id': 1,
            'email': 'admin@system.local',
            'path': '',
            'expected': '/data/file_manager'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        try:
            result = security_service.sanitize_path_for_user(
                case['user_id'],
                case['email'],
                case['path']
            )
            
            print(f"  测试 {i}: {case['path']} -> {result}")
            
            # 验证结果
            if 'expected' in case:
                if result == case['expected']:
                    print(f"    ✅ 通过")
                else:
                    print(f"    ❌ 失败: 期望 {case['expected']}, 实际 {result}")
            elif 'expected_prefix' in case:
                if result.startswith(case['expected_prefix']):
                    print(f"    ✅ 通过")
                else:
                    print(f"    ❌ 失败: 期望以 {case['expected_prefix']} 开头, 实际 {result}")
            
        except Exception as e:
            print(f"    ❌ 异常: {e}")
    
    # 测试普通用户的路径处理
    print("\n📋 测试普通用户路径处理:")
    
    test_cases_user = [
        {
            'user_id': 2,
            'email': 'test@example.com',
            'path': 'test.txt',
            'expected_prefix': '/data/file_manager/home/users/test'
        },
        {
            'user_id': 2,
            'email': 'test@example.com',
            'path': 'folder/test.txt',
            'expected_prefix': '/data/file_manager/home/users/test'
        },
        {
            'user_id': 2,
            'email': 'test@example.com',
            'path': '.',
            'expected_prefix': '/data/file_manager/home/users/test'
        }
    ]
    
    for i, case in enumerate(test_cases_user, 1):
        try:
            result = security_service.sanitize_path_for_user(
                case['user_id'],
                case['email'],
                case['path']
            )
            
            print(f"  测试 {i}: {case['path']} -> {result}")
            
            # 验证结果
            if result.startswith(case['expected_prefix']):
                print(f"    ✅ 通过")
            else:
                print(f"    ❌ 失败: 期望以 {case['expected_prefix']} 开头, 实际 {result}")
            
        except Exception as e:
            print(f"    ❌ 异常: {e}")

def test_file_operations():
    """测试文件操作路径处理"""
    print("\n🔧 测试文件操作路径处理...")
    
    from services.file_service import FileService
    
    file_service = FileService()
    
    # 模拟管理员用户
    current_user = {
        'user_id': 1,
        'email': 'admin@system.local'
    }
    
    # 测试路径清理
    test_path = 'README.txt'
    
    try:
        # 直接测试路径清理
        from services.security_service import get_security_service
        security_service = get_security_service()
        
        sanitized_path = security_service.sanitize_path_for_user(
            current_user['user_id'],
            current_user['email'],
            test_path
        )
        
        print(f"  原始路径: {test_path}")
        print(f"  清理后路径: {sanitized_path}")
        
        # 检查文件是否存在
        if os.path.exists(sanitized_path):
            print(f"  ✅ 文件存在: {sanitized_path}")
        else:
            print(f"  ❌ 文件不存在: {sanitized_path}")
            
            # 检查目录是否存在
            dir_path = os.path.dirname(sanitized_path)
            if os.path.exists(dir_path):
                print(f"  📁 目录存在: {dir_path}")
                # 列出目录内容
                try:
                    files = os.listdir(dir_path)
                    print(f"  📋 目录内容: {files}")
                except Exception as e:
                    print(f"  ❌ 无法列出目录内容: {e}")
            else:
                print(f"  ❌ 目录不存在: {dir_path}")
        
    except Exception as e:
        print(f"  ❌ 测试异常: {e}")

def main():
    """主函数"""
    print("🚀 开始路径清理功能测试...")
    print("=" * 60)
    
    try:
        # 运行测试
        test_path_sanitization()
        test_file_operations()
        
        print("\n" + "=" * 60)
        print("✅ 路径清理功能测试完成")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
