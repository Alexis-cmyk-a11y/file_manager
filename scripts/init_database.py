#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL数据库初始化脚本
用于创建数据库和初始化表结构
"""

import os
import sys
import pymysql
from pymysql.cursors import DictCursor

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='z6tsJw9NqvsDy6vZ',
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute("CREATE DATABASE IF NOT EXISTS file_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("✅ 数据库 'file_manager' 创建成功")
            
            # 使用数据库
            cursor.execute("USE file_manager")
            print("✅ 已切换到 'file_manager' 数据库")
            
            # 创建文件信息表
            create_files_table(cursor)
            
            # 创建文件操作日志表
            create_file_operations_table(cursor)
            
            # 创建用户会话表
            create_user_sessions_table(cursor)
            
            # 创建系统配置表
            create_system_configs_table(cursor)
            
            # 创建用户个人空间表
            create_user_spaces_table(cursor)
            
            # 创建共享文件表
            create_shared_files_table(cursor)
            
            # 创建索引
            create_indexes(cursor)
            
            # 插入初始配置数据
            insert_initial_data(cursor)
            
            connection.commit()
            print("✅ 所有表创建完成")
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        if 'connection' in locals():
            connection.rollback()
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()

def create_files_table(cursor):
    """创建文件信息表"""
    sql = """
    CREATE TABLE IF NOT EXISTS files (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        file_path VARCHAR(1000) NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        file_size BIGINT NOT NULL,
        file_type VARCHAR(100),
        mime_type VARCHAR(200),
        hash_value VARCHAR(64),
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        modified_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        is_directory BOOLEAN DEFAULT FALSE,
        parent_path VARCHAR(1000),
        owner VARCHAR(100),
        INDEX idx_file_path (file_path(191)),
        INDEX idx_file_name (file_name),
        INDEX idx_created_time (created_time),
        INDEX idx_modified_time (modified_time),
        INDEX idx_owner (owner),
        UNIQUE KEY uk_file_path (file_path(191))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 文件信息表创建成功")

def create_file_operations_table(cursor):
    """创建文件操作日志表"""
    sql = """
    CREATE TABLE IF NOT EXISTS file_operations (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        operation_type ENUM('upload', 'download', 'delete', 'rename', 'move', 'copy', 'create_folder', 'list_directory', 'get_file_info', 'search') NOT NULL,
        file_path VARCHAR(1000),
        file_name VARCHAR(255),
        file_size BIGINT,
        user_ip VARCHAR(45),
        user_agent TEXT,
        operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        status ENUM('success', 'failed', 'pending') DEFAULT 'success',
        error_message TEXT,
        duration_ms INT,
        INDEX idx_operation_type (operation_type),
        INDEX idx_file_path (file_path(191)),
        INDEX idx_operation_time (operation_time),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 文件操作日志表创建成功")

def create_user_sessions_table(cursor):
    """创建用户会话表"""
    sql = """
    CREATE TABLE IF NOT EXISTS user_sessions (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(255) NOT NULL,
        user_ip VARCHAR(45),
        user_agent TEXT,
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        expires_at DATETIME NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        INDEX idx_session_id (session_id),
        INDEX idx_user_ip (user_ip),
        INDEX idx_expires_at (expires_at),
        INDEX idx_is_active (is_active)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 用户会话表创建成功")

def create_system_configs_table(cursor):
    """创建系统配置表"""
    sql = """
    CREATE TABLE IF NOT EXISTS system_configs (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        config_key VARCHAR(255) NOT NULL,
        config_value TEXT,
        config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
        description TEXT,
        is_active BOOLEAN DEFAULT TRUE,
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_config_key (config_key),
        INDEX idx_is_active (is_active),
        UNIQUE KEY uk_config_key (config_key)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 系统配置表创建成功")

def create_user_spaces_table(cursor):
    """创建用户个人空间表"""
    sql = """
    CREATE TABLE IF NOT EXISTS user_spaces (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        user_id BIGINT NOT NULL,
        username VARCHAR(100) NOT NULL,
        space_path VARCHAR(1000) NOT NULL,
        created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_user_id (user_id),
        INDEX idx_username (username),
        INDEX idx_space_path (space_path(191)),
        UNIQUE KEY uk_user_id (user_id),
        UNIQUE KEY uk_username (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 用户个人空间表创建成功")

def create_shared_files_table(cursor):
    """创建共享文件表"""
    sql = """
    CREATE TABLE IF NOT EXISTS shared_files (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        original_file_path VARCHAR(1000) NOT NULL,
        shared_file_path VARCHAR(1000) NOT NULL,
        owner_username VARCHAR(100) NOT NULL,
        shared_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        INDEX idx_original_path (original_file_path(191)),
        INDEX idx_shared_path (shared_file_path(191)),
        INDEX idx_owner (owner_username),
        INDEX idx_is_active (is_active),
        UNIQUE KEY uk_shared_path (shared_file_path(191))
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """
    cursor.execute(sql)
    print("✅ 共享文件表创建成功")

def create_indexes(cursor):
    """创建额外的索引"""
    try:
        # 为文件操作日志表添加复合索引
        cursor.execute("""
        CREATE INDEX idx_operation_type_time ON file_operations (operation_type, operation_time)
        """)
        print("✅ 复合索引创建成功")
    except Exception as e:
        print(f"⚠️  复合索引创建失败（可能已存在）: {e}")

def insert_initial_data(cursor):
    """插入初始配置数据"""
    try:
        # 插入系统配置
        configs = [
            ('system.version', '2.0.0', 'string', '系统版本号'),
            ('system.name', '文件管理系统', 'string', '系统名称'),
            ('system.description', '基于Flask的现代化文件管理系统', 'string', '系统描述'),
            ('upload.max_file_size', '1073741824', 'number', '最大上传文件大小（字节）'),
            ('upload.allowed_extensions', '', 'string', '允许上传的文件扩展名（空表示允许所有）'),
            ('security.enable_file_type_detection', 'true', 'boolean', '是否启用文件类型检测'),
            ('cache.default_ttl', '300', 'number', '默认缓存时间（秒）'),
            ('logging.level', 'INFO', 'string', '日志级别'),
            ('mysql.connection_pool_size', '20', 'number', 'MySQL连接池大小'),
            ('redis.connection_pool_size', '20', 'number', 'Redis连接池大小')
        ]
        
        for config_key, config_value, config_type, description in configs:
            cursor.execute("""
            INSERT IGNORE INTO system_configs (config_key, config_value, config_type, description)
            VALUES (%s, %s, %s, %s)
            """, (config_key, config_value, config_type, description))
        
        print("✅ 初始配置数据插入成功")
        
    except Exception as e:
        print(f"⚠️  初始数据插入失败: {e}")

def test_connection():
    """测试数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='z6tsJw9NqvsDy6vZ',
            database='file_manager',
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            if result and result['test'] == 1:
                print("✅ 数据库连接测试成功")
                return True
            else:
                print("❌ 数据库连接测试失败")
                return False
                
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """主函数"""
    print("🚀 开始初始化MySQL数据库...")
    print("=" * 50)
    
    # 创建数据库和表
    create_database()
    
    print("=" * 50)
    print("🧪 测试数据库连接...")
    
    # 测试连接
    if test_connection():
        print("🎉 数据库初始化完成！")
        print("\n📋 已创建的表:")
        print("   - files (文件信息表)")
        print("   - file_operations (文件操作日志表)")
        print("   - user_sessions (用户会话表)")
        print("   - system_configs (系统配置表)")
        print("   - user_spaces (用户个人空间表)")
        print("   - shared_files (共享文件表)")
        print("\n🔧 下一步:")
        print("   1. 启动文件管理系统: python main.py")
        print("   2. 访问: http://localhost:8888")
        print("   3. 系统将自动使用MySQL存储文件信息和操作日志")
    else:
        print("❌ 数据库初始化失败，请检查配置和连接")

if __name__ == '__main__':
    main()
