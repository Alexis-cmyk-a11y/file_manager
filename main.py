#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理系统主程序入口
使用配置文件管理，支持多环境配置
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.app import create_app
from core.config_manager import config_manager
from utils.logger import get_logger

def main():
    """主函数"""
    # 获取日志记录器
    logger = get_logger('file_manager.main')
    
    try:
        start_time = time.time()
        
        # 显示启动信息
        print("🚀 启动文件管理系统...")
        print(f"📁 项目根目录: {project_root}")
        print(f"⚙️  配置目录: {config_manager.config_dir}")
        print(f"🌍 运行环境: {config_manager.environment}")
        print()
        
        # 打印配置摘要
        config_manager.print_config_summary()
        
        # 创建应用实例
        logger.info("正在创建应用实例...")
        app = create_app()
        
        # 获取配置
        server_config = config_manager.get_server_config()
        host = server_config.host
        port = server_config.port
        debug = server_config.debug
        
        # 记录启动信息
        logger.info(
            "文件管理系统启动",
            operation="system_startup",
            host=host,
            port=port,
            debug_mode=debug,
            config_source="config_manager",
            environment=config_manager.environment
        )
        
        # 控制台输出
        print(f"📍 访问地址: http://{host}:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print("⏹️  按 Ctrl+C 停止服务")
        print()
        
        # 显示功能模块状态
        print("📋 功能模块启动状态:")
        print("   ✅ 文件管理 - 浏览、上传、下载、重命名")
        print("   ✅ 在线编辑 - CodeMirror编辑器，支持50+种编程语言")
        print("   ✅ 系统监控 - 磁盘使用、内存状态")
        print("   ✅ 安全防护 - 路径验证、文件类型检查")
        print("   ✅ 用户认证 - 注册、登录、邮箱验证码、权限管理")
        print("   ✅ 日志系统 - 结构化日志、JSON格式、自动轮转")
        print("   ✅ MySQL数据库 - 文件信息存储、操作日志、用户会话")
        print("   ✅ Redis缓存 - 高性能缓存、连接池管理")
        print("   ✅ 日志维护 - 30天自动清理、表性能优化")
        print("   ✅ 网络下载 - 公网文件下载到服务器download目录")
        print()
        
        # 显示配置特性
        print("⚙️  配置系统特性:")
        print("   ✅ 多环境配置 - 开发、生产、测试环境")
        print("   ✅ 配置热重载 - 修改配置无需重启")
        print("   ✅ 配置验证 - 自动验证配置有效性")
        print("   ✅ 前端配置 - 主题、功能、编辑器配置")
        print("   ✅ 性能监控 - 响应时间、资源使用监控")
        print()
        
        # 显示在线编辑器信息
        print("💡 在线编辑器使用:")
        print(f"   编辑器页面: http://{host}:{port}/editor")
        print("   支持文件: .py, .js, .html, .css, .md, .json 等")
        print("   快捷键: Ctrl+S(保存), Ctrl+F(搜索), Ctrl+Z(撤销)")
        print()
        
        # 显示用户认证系统信息
        print("🔐 用户认证系统:")
        print(f"   登录页面: http://{host}:{port}/login")
        print(f"   注册页面: http://{host}:{port}/register")
        print("   默认管理员: admin@system.local / Asdasd123")
        print()
        
        # 显示日志系统信息
        logging_config = config_manager.get_logging_config()
        print("📊 日志系统:")
        print(f"   日志文件: {logging_config.file}")
        print(f"   日志级别: {logging_config.level}")
        print(f"   日志格式: {logging_config.format}")
        print(f"   控制台输出: {'开启' if logging_config.console.get('enabled', True) else '关闭'}")
        print(f"   文件输出: {'开启' if logging_config.file_config.get('enabled', True) else '关闭'}")
        print()
        
        # 显示数据库信息
        db_config = config_manager.get_database_config()
        print("💾 数据库配置:")
        print(f"   MySQL: {db_config.mysql.get('host', 'localhost')}:{db_config.mysql.get('port', 3306)}")
        print(f"   Redis: {db_config.redis.get('host', 'localhost')}:{db_config.redis.get('port', 6379)}")
        print(f"   缓存: {'开启' if config_manager.get('cache.enabled', True) else '关闭'}")
        print()
        
        # 显示前端配置信息
        frontend_config = config_manager.get_frontend_config()
        print("🎨 前端配置:")
        print(f"   应用名称: {frontend_config.app_name}")
        print(f"   主题色彩: {frontend_config.theme.get('primary_color', '#4a6fa5')}")
        print(f"   默认视图: {frontend_config.features.get('default_view', 'list')}")
        print(f"   页面大小: {frontend_config.features.get('page_size', 50)}")
        print()
        
        # 启动应用
        logger.info("正在启动Flask应用...")
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # 避免重复启动
        )
        
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭服务...")
        print("\n🛑 服务已停止")
    except Exception as e:
        logger.critical(
            "应用启动失败",
            operation="system_startup_failed",
            error=str(e),
            error_type=type(e).__name__,
            environment=config_manager.environment
        )
        print(f"❌ 启动失败: {e}")
        print(f"🔍 错误类型: {type(e).__name__}")
        print(f"📁 配置目录: {config_manager.config_dir}")
        print(f"🌍 运行环境: {config_manager.environment}")
        sys.exit(1)
    finally:
        # 记录运行时间
        if 'start_time' in locals():
            run_time = time.time() - start_time
            logger.info(
                "应用运行结束",
                operation="system_shutdown",
                run_time_seconds=round(run_time, 2),
                environment=config_manager.environment
            )

if __name__ == '__main__':
    main()
