#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理系统主程序入口
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.app import create_app
from core.config import Config

def main():
    """主函数"""
    try:
        # 创建应用实例
        app = create_app(Config)
        
        # 获取配置
        host = app.config.get('SERVER_HOST', '127.0.0.1')
        port = app.config.get('SERVER_PORT', 5000)
        debug = app.config.get('DEBUG_MODE', False)
        
        print(f"启动文件管理系统...")
        print(f"访问地址: http://{host}:{port}")
        print(f"调试模式: {'开启' if debug else '关闭'}")
        print("按 Ctrl+C 停止服务")
        
        # 启动应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # 避免重复启动
        )
        
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
