#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化简单文件管理系统
设置目录结构和数据库，移除权限系统
"""

import os
import sys
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def create_directory_structure():
    """创建目录结构"""
    print("📁 创建目录结构...")
    
    # 基础目录
    base_dirs = [
        'home/users',
        'home/shared',
        'home/admin',
        'download',
        'logs',
        'public'
    ]
    
    for dir_path in base_dirs:
        full_path = os.path.join(project_root, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"   ✅ 创建目录: {dir_path}")
    
    # 创建示例用户目录
    sample_users = ['admin', 'test', 'demo']
    for user in sample_users:
        user_dir = os.path.join(project_root, 'home', 'users', user)
        shared_dir = os.path.join(project_root, 'home', 'shared', f'{user}_shared')
        
        os.makedirs(user_dir, exist_ok=True)
        os.makedirs(shared_dir, exist_ok=True)
        
        # 设置共享目录权限为只读
        os.chmod(shared_dir, 0o755)
        
        print(f"   ✅ 创建用户目录: home/users/{user}")
        print(f"   ✅ 创建共享目录: home/shared/{user}_shared")
    
    # 创建示例文件
    sample_files = [
        ('home/admin/README.md', '# 管理员目录\n\n这是系统管理员的工作目录。'),
        ('home/admin/system_info.txt', '系统信息文件\n\n版本: 2.0.0\n状态: 运行中'),
        ('home/test/test.txt', '这是一个测试文件\n\n用于测试文件管理系统的基本功能。'),
        ('home/demo/hello.py', '#!/usr/bin/env python3\n\nprint("Hello, File Manager!")\n\n# 这是一个示例Python文件'),
        ('home/demo/example.md', '# 示例文档\n\n这是一个Markdown格式的示例文档。')
    ]
    
    for file_path, content in sample_files:
        full_path = os.path.join(project_root, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ 创建示例文件: {file_path}")

def cleanup_old_permission_files():
    """清理旧的权限相关文件"""
    print("\n🧹 清理旧的权限相关文件...")
    
    # 需要删除的文件和目录
    files_to_delete = [
        'services/permission_service.py',
        'utils/permission_middleware.py',
        'api/routes/permission.py',
        'templates/permission_manager.html',
        'scripts/fix_admin_permissions.py',
        'scripts/fix_user_permissions.py',
        'scripts/setup_permissions.py',
        'scripts/quick_start_permission.py',
        'scripts/test_permission_integration.py'
    ]
    
    for file_path in files_to_delete:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"   ✅ 删除文件: {file_path}")
            except Exception as e:
                print(f"   ⚠️  删除失败: {file_path} - {e}")
        else:
            print(f"   ℹ️  文件不存在: {file_path}")

def update_database():
    """更新数据库结构"""
    print("\n💾 更新数据库结构...")
    
    try:
        # 运行数据库初始化脚本
        from scripts.init_database import create_database
        create_database()
        print("   ✅ 数据库结构更新完成")
    except Exception as e:
        print(f"   ❌ 数据库更新失败: {e}")
        print("   💡 请手动运行: python scripts/init_database.py")

def create_readme():
    """创建新的README文件"""
    print("\n📝 创建新的README文件...")
    
    readme_content = """# 文件管理系统 - 简化版

## 概述

这是一个基于目录隔离和硬链接共享的简单文件管理系统，替代了复杂的权限系统。

## 系统架构

### 目录结构
```
/home/
   ├── users/           # 用户个人目录
   │    ├── username1/  # 用户1的独立空间
   │    ├── username2/  # 用户2的独立空间
   │    └── ...
   ├── shared/          # 共享文件区域
   │    ├── username1_shared/  # 用户1的共享文件
   │    ├── username2_shared/  # 用户2的共享文件
   │    └── ...
   └── admin/           # 管理员目录（全局访问）
```

### 权限机制

- **用户隔离**: 每个用户只能访问自己的目录和共享区域
- **文件共享**: 基于硬链接实现，节省磁盘空间
- **共享控制**: 共享区文件只读，原文件完全控制
- **自动同步**: 原文件修改自动反映到共享区

## 主要功能

- ✅ 文件管理（上传、下载、删除、重命名）
- ✅ 在线编辑（支持多种编程语言）
- ✅ 文件共享（基于硬链接）
- ✅ 用户认证（注册、登录）
- ✅ 目录浏览和搜索

## 快速开始

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **初始化数据库**
   ```bash
   python scripts/init_database.py
   ```

3. **启动系统**
   ```bash
   python main.py
   ```

4. **访问系统**
   - 主页: http://localhost:8888
   - 共享文件: http://localhost:8888/shared
   - 在线编辑: http://localhost:8888/editor

## API接口

### 文件共享
- `POST /api/sharing/share` - 共享文件
- `POST /api/sharing/unshare` - 取消共享
- `GET /api/sharing/shared` - 获取共享文件列表
- `GET /api/sharing/status/<username>/<path>` - 检查共享状态

### 文件操作
- `GET /api/list` - 列出目录内容
- `POST /api/upload` - 上传文件
- `GET /api/download` - 下载文件
- `DELETE /api/delete` - 删除文件
- `POST /api/share` - 共享文件
- `POST /api/unshare` - 取消共享

## 配置说明

系统使用配置文件管理，支持多环境配置：
- `config/development.yaml` - 开发环境
- `config/production.yaml` - 生产环境

## 技术栈

- **后端**: Python + Flask
- **数据库**: MySQL + Redis
- **前端**: HTML + CSS + JavaScript
- **编辑器**: CodeMirror
- **文件共享**: 硬链接机制

## 注意事项

1. 系统使用硬链接实现文件共享，确保文件系统支持硬链接
2. 共享目录设置为只读权限，防止误操作
3. 用户目录完全隔离，确保安全性
4. 支持自动清理孤立的共享文件

## 许可证

MIT License
"""
    
    readme_path = os.path.join(project_root, 'README_SIMPLE.md')
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"   ✅ 创建README文件: README_SIMPLE.md")

def main():
    """主函数"""
    print("🚀 开始初始化简单文件管理系统...")
    print("=" * 60)
    
    # 创建目录结构
    create_directory_structure()
    
    # 清理旧文件
    cleanup_old_permission_files()
    
    # 更新数据库
    update_database()
    
    # 创建README
    create_readme()
    
    print("\n" + "=" * 60)
    print("🎉 简单文件管理系统初始化完成！")
    print("\n📋 下一步操作:")
    print("   1. 启动系统: python main.py")
    print("   2. 访问: http://localhost:8888")
    print("   3. 查看共享文件: http://localhost:8888/shared")
    print("   4. 在线编辑: http://localhost:8888/editor")
    print("\n📚 相关文档:")
    print("   - 系统说明: README_SIMPLE.md")
    print("   - 共享机制: home/admin/roles.md")
    print("\n🔧 注意事项:")
    print("   - 确保MySQL和Redis服务正在运行")
    print("   - 检查配置文件中的数据库连接信息")
    print("   - 系统使用硬链接实现文件共享")

if __name__ == '__main__':
    main()
