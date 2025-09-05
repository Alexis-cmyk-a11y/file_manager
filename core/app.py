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
from flask_session import Session

from core.config import Config
from utils.logger import setup_logging, get_logger

# 全局limiter实例
limiter = None

def create_app(config_class=Config):
    """创建Flask应用实例"""
    global limiter
    
    app = Flask(__name__)
    
    # 配置应用
    app.config.from_object(config_class())
    
    # 配置session
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时
    
    # 使用临时目录存储session文件
    import tempfile
    session_dir = tempfile.mkdtemp(prefix='file_manager_session_')
    app.config['SESSION_FILE_DIR'] = session_dir
    
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
    
    # 初始化Flask-Session
    Session(app)
    
    # 初始化速率限制器
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[config_class.RATE_LIMIT] if hasattr(config_class, 'RATE_LIMIT') else ["100 per minute"]
    )
    
    # 初始化Redis服务
    try:
        from services.redis_service import get_redis_service, close_redis_service
        redis_service = get_redis_service()
        if redis_service.is_connected():
            app.logger.info("Redis服务初始化成功")
            app.redis_service = redis_service
        else:
            app.logger.warning("Redis服务初始化失败，将使用内存存储")
            app.redis_service = None
    except Exception as e:
        app.logger.error(f"Redis服务初始化错误: {e}")
        app.redis_service = None
    
    # 初始化MySQL服务
    try:
        from services.mysql_service import get_mysql_service, close_mysql_service
        mysql_service = get_mysql_service()
        if mysql_service.is_connected():
            app.logger.info("MySQL服务初始化成功")
            app.mysql_service = mysql_service
            
            # 创建必要的数据库表
            try:
                mysql_service.create_tables()
                app.logger.info("MySQL数据库表创建完成")
                
                # 创建管理员账户
                try:
                    from services.auth_service import get_auth_service
                    auth_service = get_auth_service()
                    if auth_service.create_admin_user():
                        app.logger.info("管理员账户创建/检查完成")
                    else:
                        app.logger.warning("管理员账户创建失败")
                except Exception as admin_error:
                    app.logger.warning(f"管理员账户创建失败: {admin_error}")
                
                # 启动日志维护服务
                try:
                    from services.log_maintenance_service import start_log_maintenance
                    if start_log_maintenance():
                        app.logger.info("日志维护服务启动成功")
                    else:
                        app.logger.warning("日志维护服务启动失败")
                except Exception as maintenance_error:
                    app.logger.warning(f"日志维护服务启动失败: {maintenance_error}")
                    
            except Exception as table_error:
                app.logger.warning(f"MySQL数据库表创建失败: {table_error}")
        else:
            app.logger.warning("MySQL服务初始化失败，数据库功能将不可用")
            app.mysql_service = None
    except Exception as e:
        app.logger.error(f"MySQL服务初始化错误: {e}")
        app.mysql_service = None
    
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
    from api.routes import file_ops, upload, download, system, editor, auth, sharing, chunked_upload
    
    app.register_blueprint(file_ops.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(download.bp)
    app.register_blueprint(system.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(chunked_upload.bp)

    app.register_blueprint(sharing.sharing_bp, url_prefix='/api/sharing')

def register_page_routes(app):
    """注册页面路由"""
    from flask import session, redirect, url_for, request, render_template
    
    def require_auth(f):
        """身份验证装饰器"""
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if 'user_id' not in session:
                    app.logger.info(f"未认证用户尝试访问: {request.path}")
                    # 使用绝对URL进行重定向
                    login_url = request.host_url.rstrip('/') + url_for('login_page')
                    return redirect(login_url, code=302)
                return f(*args, **kwargs)
            except Exception as e:
                app.logger.error(f"身份验证装饰器错误: {e}")
                # 如果重定向失败，返回错误页面
                return render_template('error.html', error='身份验证失败，请重新登录'), 401
        return decorated_function
    
    @app.route('/')
    @require_auth
    def index():
        """主页 - 文件管理器（需要登录）"""
        app.logger.info(f"用户访问首页，session: {dict(session)}")
        return render_template('index.html')
    
    @app.route('/editor')
    @require_auth
    def editor_page():
        """编辑器页面（需要登录）"""
        return render_template('editor.html')
    
    @app.route('/shared')
    @require_auth
    def shared_files_page():
        """共享文件页面（需要登录）"""
        return render_template('shared_files.html')
    
    @app.route('/upload-manager')
    @require_auth
    def upload_manager_page():
        """上传管理页面（需要登录）"""
        return render_template('upload_manager.html')
    
    @app.route('/login')
    def login_page():
        """登录页面"""
        return render_template('login.html')
    
    @app.route('/reset-password')
    def reset_password_page():
        """重置密码页面"""
        return render_template('reset_password.html')
    
    @app.route('/register')
    def register_page():
        """注册页面"""
        return render_template('register.html')
    
    @app.route('/logout')
    def logout():
        """登出功能"""
        try:
            # 记录登出信息
            user_email = session.get('email', 'unknown')
            app.logger.info(f"用户登出: {user_email}")
            
            # 清除session
            session.clear()
            
            # 使用绝对URL进行重定向，避免相对路径问题
            login_url = request.host_url.rstrip('/') + url_for('login_page')
            app.logger.info(f"重定向到登录页面: {login_url}")
            
            return redirect(login_url, code=302)
            
        except Exception as e:
            app.logger.error(f"登出过程中发生错误: {e}")
            # 如果重定向失败，返回JSON响应
            return {'success': False, 'message': '登出失败，请手动访问登录页面'}, 500
    
    @app.route('/health')
    def health_check():
        """健康检查端点（无需认证）"""
        return {'status': 'healthy', 'message': '文件管理系统运行正常'}
    


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
