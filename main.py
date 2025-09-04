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
