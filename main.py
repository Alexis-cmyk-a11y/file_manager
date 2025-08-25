#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理系统主程序入口
"""

import os
import sys
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.app import create_app
from core.config import Config
from utils.logger import get_logger

def main():
    """主函数"""
    # 获取日志记录器
    logger = get_logger('file_manager.main')
    
    try:
        start_time = time.time()
        
        # 创建应用实例
        logger.info("正在创建应用实例...")
        app = create_app(Config)
        
        # 获取配置
        host = app.config.get('SERVER_HOST', '127.0.0.1')
        port = app.config.get('SERVER_PORT', 5000)
        debug = app.config.get('DEBUG_MODE', False)
        
        # 记录启动信息
        logger.info(
            "文件管理系统启动",
            operation="system_startup",
            host=host,
            port=port,
            debug_mode=debug,
            config_source="Config"
        )
        
        
        # 控制台输出
        print(f"🚀 启动文件管理系统...")
        print(f"📍 访问地址: http://{host}:{port}")
        print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
        print("⏹️  按 Ctrl+C 停止服务")
        print()
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
        print("💡 在线编辑器使用:")
        print(f"   编辑器页面: http://{host}:{port}/editor")
        print("   支持文件: .py, .js, .html, .css, .md, .json 等")
        print("   快捷键: Ctrl+S(保存), Ctrl+F(搜索), Ctrl+Z(撤销)")
        print()
        print("🔐 用户认证系统:")
        print(f"   登录页面: http://{host}:{port}/login")
        print(f"   注册页面: http://{host}:{port}/register")
        print("   默认管理员: admin@system.local / Asdasd123")
        print()
        print("📊 日志系统:")
        print(f"   日志文件: {app.config.get('LOG_FILE', 'logs/file_manager.log')}")
        print(f"   日志级别: {app.config.get('LOG_LEVEL', 'INFO')}")
        print(f"   日志格式: {app.config.get('LOG_FORMAT', 'json')}")
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
            error_type=type(e).__name__
        )
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    finally:
        # 记录运行时间
        if 'start_time' in locals():
            run_time = time.time() - start_time
            logger.info(
                "应用运行结束",
                operation="system_shutdown",
                run_time_seconds=round(run_time, 2)
            )

if __name__ == '__main__':
    main()
