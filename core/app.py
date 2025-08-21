"""
文件管理系统应用工厂
提供Flask应用的创建和配置
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config

# 全局limiter实例
limiter = None

def create_app(config_class=Config):
    """创建Flask应用实例"""
    global limiter
    
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_object(config_class)
    
    # 处理打包后的资源路径
    def resource_path(relative_path):
        """获取打包后资源的绝对路径"""
        try:
            # PyInstaller创建的临时文件夹中的路径
            base_path = sys._MEIPASS
        except Exception:
            # 正常开发环境路径
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    # 设置静态文件和模板路径
    app.static_folder = resource_path('static')
    app.template_folder = resource_path('templates')
    
    # 配置日志
    setup_logging(app, config_class)
    
    # 启用CORS
    CORS(app)
    
    # 初始化速率限制器
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[config_class.RATE_LIMIT] if hasattr(config_class, 'RATE_LIMIT') else ["100 per minute"]
    )
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册中间件
    register_middleware(app)
    
    return app

def setup_logging(app, config_class):
    """配置应用日志"""
    log_level = getattr(logging, config_class.LOG_LEVEL)
    log_formatter = logging.Formatter(config_class.LOG_FORMAT)
    
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        config_class.LOG_FILE, 
        maxBytes=config_class.LOG_MAX_SIZE, 
        backupCount=config_class.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_formatter)
    
    # 配置应用日志
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    app.logger.addHandler(console_handler)
    
    app.logger.info("应用启动，根目录设置为: %s", config_class.ROOT_DIR)

def register_blueprints(app):
    """注册蓝图"""
    from api.routes import file_ops, upload, download, system
    
    app.register_blueprint(file_ops.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(system.bp)

def register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(413)
    def too_large(e):
        """文件过大错误处理"""
        return {'success': False, 'message': '上传的文件过大'}, 413

    @app.errorhandler(404)
    def not_found(e):
        """404错误处理"""
        return {'success': False, 'message': '请求的资源不存在'}, 404

    @app.errorhandler(500)
    def internal_error(e):
        """500错误处理"""
        app.logger.error(f"内部服务器错误: {str(e)}")
        return {'success': False, 'message': '内部服务器错误'}, 500

def register_middleware(app):
    """注册中间件"""
    # 这里可以添加自定义中间件
    pass
