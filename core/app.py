"""
文件管理系统应用工厂
提供Flask应用的创建和配置
"""

import os
import sys
from flask import Flask, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.config import Config
from utils.logger import setup_logging, get_logger

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
    
    # 配置日志系统
    logger_manager = setup_logging(config_class())
    app.logger_manager = logger_manager
    
    # 获取应用日志记录器
    app.logger = get_logger('file_manager.app')
    
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
    
    # 注册页面路由
    register_page_routes(app)
    
    return app



def register_blueprints(app):
    """注册蓝图"""
    from api.routes import file_ops, upload, download, system, editor
    
    app.register_blueprint(file_ops.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(system.bp)
    app.register_blueprint(editor.bp)

def register_page_routes(app):
    """注册页面路由"""
    @app.route('/')
    def index():
        """主页 - 文件管理器"""
        return render_template('index.html')
    
    @app.route('/editor')
    def editor_page():
        """编辑器页面"""
        return render_template('editor.html')
    
    @app.route('/debug')
    def debug_page():
        """调试页面"""
        return render_template('test_editor_debug.html')
    
    @app.route('/test_markdown')
    def test_markdown_page():
        """Markdown预览功能测试页面"""
        return render_template('test_markdown.html')
    
    @app.route('/LICENSE')
    def license_file():
        """提供LICENSE文件"""
        try:
            with open('LICENSE', 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        except FileNotFoundError:
            return 'License file not found', 404
    
    @app.route('/CONTRIBUTING.md')
    def contributing_file():
        """提供CONTRIBUTING.md文件"""
        try:
            with open('CONTRIBUTING.md', 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/markdown; charset=utf-8'}
        except FileNotFoundError:
            return 'Contributing file not found', 404

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
