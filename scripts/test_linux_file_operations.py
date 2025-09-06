#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux文件操作测试脚本
测试重命名、删除、移动、复制等操作在Linux环境下的兼容性
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.file_service import FileService
from services.security_service import get_security_service
from utils.logger import get_logger

logger = get_logger(__name__)

def create_test_environment():
    """创建测试环境"""
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix='file_manager_test_')
    
    # 创建测试文件结构
    test_files = {
        'test_file.txt': '这是一个测试文件',
        'test_folder': {
            'nested_file.txt': '嵌套文件内容',
            'another_file.log': '日志文件内容'
        }
    }
    
    def create_files(base_path, files):
        for name, content in files.items():
            file_path = os.path.join(base_path, name)
            if isinstance(content, dict):
                # 创建目录
                os.makedirs(file_path, exist_ok=True)
                create_files(file_path, content)
            else:
                # 创建文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    create_files(test_dir, test_files)
    
    return test_dir

def test_rename_operation(test_dir):
    """测试重命名操作"""
    print("\n🔄 测试重命名操作...")
    
    file_service = FileService()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    # 测试文件重命名
    old_file = os.path.join(test_dir, 'test_file.txt')
    new_name = 'renamed_file.txt'
    
    try:
        result = file_service.rename_file(
            old_file, 
            new_name, 
            current_user=current_user
        )
        
        if result['success']:
            print(f"✅ 文件重命名成功: {old_file} -> {result['new_path']}")
            
            # 验证文件确实被重命名
            if os.path.exists(result['new_path']):
                print("✅ 重命名后的文件存在")
            else:
                print("❌ 重命名后的文件不存在")
                return False
        else:
            print(f"❌ 文件重命名失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 重命名操作异常: {e}")
        return False
    
    # 测试文件夹重命名
    old_folder = os.path.join(test_dir, 'test_folder')
    new_folder_name = 'renamed_folder'
    
    try:
        result = file_service.rename_file(
            old_folder, 
            new_folder_name, 
            current_user=current_user
        )
        
        if result['success']:
            print(f"✅ 文件夹重命名成功: {old_folder} -> {result['new_path']}")
            
            # 验证文件夹确实被重命名
            if os.path.exists(result['new_path']):
                print("✅ 重命名后的文件夹存在")
            else:
                print("❌ 重命名后的文件夹不存在")
                return False
        else:
            print(f"❌ 文件夹重命名失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 文件夹重命名操作异常: {e}")
        return False
    
    return True

def test_delete_operation(test_dir):
    """测试删除操作"""
    print("\n🗑️  测试删除操作...")
    
    file_service = FileService()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    # 创建要删除的文件
    file_to_delete = os.path.join(test_dir, 'file_to_delete.txt')
    with open(file_to_delete, 'w') as f:
        f.write('这个文件将被删除')
    
    try:
        result = file_service.delete_file(
            file_to_delete, 
            current_user=current_user
        )
        
        if result['success']:
            print(f"✅ 文件删除成功: {file_to_delete}")
            
            # 验证文件确实被删除
            if not os.path.exists(file_to_delete):
                print("✅ 文件已被成功删除")
            else:
                print("❌ 文件仍然存在")
                return False
        else:
            print(f"❌ 文件删除失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 删除操作异常: {e}")
        return False
    
    return True

def test_move_operation(test_dir):
    """测试移动操作"""
    print("\n📁 测试移动操作...")
    
    file_service = FileService()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    # 创建要移动的文件
    source_file = os.path.join(test_dir, 'file_to_move.txt')
    with open(source_file, 'w') as f:
        f.write('这个文件将被移动')
    
    # 创建目标目录
    target_dir = os.path.join(test_dir, 'target_dir')
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, 'moved_file.txt')
    
    try:
        result = file_service.move_file(
            source_file, 
            target_file, 
            current_user=current_user
        )
        
        if result['success']:
            print(f"✅ 文件移动成功: {source_file} -> {target_file}")
            
            # 验证文件确实被移动
            if os.path.exists(target_file) and not os.path.exists(source_file):
                print("✅ 文件已被成功移动")
            else:
                print("❌ 文件移动失败")
                return False
        else:
            print(f"❌ 文件移动失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 移动操作异常: {e}")
        return False
    
    return True

def test_copy_operation(test_dir):
    """测试复制操作"""
    print("\n📋 测试复制操作...")
    
    file_service = FileService()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    # 创建要复制的文件
    source_file = os.path.join(test_dir, 'file_to_copy.txt')
    with open(source_file, 'w') as f:
        f.write('这个文件将被复制')
    
    # 创建目标目录
    target_dir = os.path.join(test_dir, 'copy_target_dir')
    os.makedirs(target_dir, exist_ok=True)
    target_file = os.path.join(target_dir, 'copied_file.txt')
    
    try:
        result = file_service.copy_file(
            source_file, 
            target_file, 
            current_user=current_user
        )
        
        if result['success']:
            print(f"✅ 文件复制成功: {source_file} -> {target_file}")
            
            # 验证文件确实被复制
            if os.path.exists(target_file) and os.path.exists(source_file):
                print("✅ 文件已被成功复制")
            else:
                print("❌ 文件复制失败")
                return False
        else:
            print(f"❌ 文件复制失败: {result['message']}")
            return False
            
    except Exception as e:
        print(f"❌ 复制操作异常: {e}")
        return False
    
    return True

def test_search_operation(test_dir):
    """测试搜索操作"""
    print("\n🔍 测试搜索操作...")
    
    file_service = FileService()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    try:
        result = file_service.search_files(
            test_dir, 
            'test', 
            current_user=current_user
        )
        
        if 'results' in result:
            print(f"✅ 搜索操作成功，找到 {len(result['results'])} 个结果")
            
            # 验证搜索结果
            if len(result['results']) > 0:
                print("✅ 搜索返回了结果")
            else:
                print("⚠️  搜索没有返回结果")
        else:
            print(f"❌ 搜索操作失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 搜索操作异常: {e}")
        return False
    
    return True

def test_path_sanitization():
    """测试路径清理功能"""
    print("\n🔒 测试路径清理功能...")
    
    security_service = get_security_service()
    
    # 模拟用户信息
    current_user = {
        'user_id': 1,
        'email': 'test@example.com'
    }
    
    test_paths = [
        '.',
        'test_file.txt',
        'folder/subfolder/file.txt',
        '/absolute/path/file.txt',
        '../outside/path/file.txt'
    ]
    
    for path in test_paths:
        try:
            sanitized_path = security_service.sanitize_path_for_user(
                current_user['user_id'],
                current_user['email'],
                path
            )
            print(f"✅ 路径清理: {path} -> {sanitized_path}")
        except Exception as e:
            print(f"❌ 路径清理失败: {path} - {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("🚀 开始Linux文件操作兼容性测试...")
    print("=" * 60)
    
    # 创建测试环境
    test_dir = create_test_environment()
    print(f"📁 测试目录: {test_dir}")
    
    try:
        # 运行所有测试
        tests = [
            ("路径清理", test_path_sanitization),
            ("重命名操作", lambda: test_rename_operation(test_dir)),
            ("删除操作", lambda: test_delete_operation(test_dir)),
            ("移动操作", lambda: test_move_operation(test_dir)),
            ("复制操作", lambda: test_copy_operation(test_dir)),
            ("搜索操作", lambda: test_search_operation(test_dir))
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                if test_func():
                    print(f"✅ {test_name} 测试通过")
                    passed += 1
                else:
                    print(f"❌ {test_name} 测试失败")
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
        
        # 显示测试结果
        print("\n" + "=" * 60)
        print("📊 测试结果摘要")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过数: {passed}")
        print(f"失败数: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！Linux文件操作兼容性良好")
            return 0
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，需要进一步检查")
            return 1
            
    finally:
        # 清理测试环境
        try:
            shutil.rmtree(test_dir)
            print(f"\n🧹 测试环境已清理: {test_dir}")
        except Exception as e:
            print(f"\n⚠️  清理测试环境失败: {e}")

if __name__ == '__main__':
    sys.exit(main())
