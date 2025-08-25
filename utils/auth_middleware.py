"""
认证中间件
为所有API端点提供统一的认证保护
"""

from functools import wraps
from flask import request, jsonify, session
from utils.logger import get_logger

logger = get_logger(__name__)

def require_auth_api(f):
    """API认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 检查用户是否已登录
            if 'user_id' not in session:
                logger.warning(f"未认证用户尝试访问API: {request.path}, IP: {request.remote_addr}")
                return jsonify({
                    'success': False,
                    'message': '用户未登录，请先登录',
                    'error_code': 'UNAUTHORIZED',
                    'redirect_url': '/login'
                }), 401
            
            # 检查session是否有效
            user_id = session.get('user_id')
            email = session.get('email')
            
            if not user_id or not email:
                logger.warning(f"无效的session数据: user_id={user_id}, email={email}")
                session.clear()
                return jsonify({
                    'success': False,
                    'message': '登录状态无效，请重新登录',
                    'error_code': 'INVALID_SESSION',
                    'redirect_url': '/login'
                }), 401
            
            # 记录API访问日志
            logger.info(f"用户访问API: {email} -> {request.path}, IP: {request.remote_addr}")
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"API认证中间件错误: {e}")
            return jsonify({
                'success': False,
                'message': '认证服务异常，请稍后重试',
                'error_code': 'AUTH_ERROR'
            }), 500
    
    return decorated_function

def require_admin(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 首先检查用户是否已登录
            if 'user_id' not in session:
                return jsonify({
                    'success': False,
                    'message': '用户未登录，请先登录',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            # 检查用户角色（这里需要从数据库获取用户角色）
            # 暂时使用session中的信息，后续可以增强
            user_id = session.get('user_id')
            email = session.get('email')
            
            # 检查是否为管理员（这里可以根据实际需求调整）
            if email != 'admin@system.local':  # 临时检查，建议从数据库获取角色
                logger.warning(f"非管理员用户尝试访问管理功能: {email} -> {request.path}")
                return jsonify({
                    'success': False,
                    'message': '权限不足，需要管理员权限',
                    'error_code': 'INSUFFICIENT_PERMISSIONS'
                }), 403
            
            logger.info(f"管理员访问API: {email} -> {request.path}")
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"管理员权限检查错误: {e}")
            return jsonify({
                'success': False,
                'message': '权限检查服务异常',
                'error_code': 'PERMISSION_ERROR'
            }), 500
    
    return decorated_function

def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return None
    
    return {
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'login_time': session.get('login_time'),
        'ip_address': session.get('ip_address')
    }

def is_authenticated():
    """检查用户是否已认证"""
    return 'user_id' in session and 'email' in session

def get_user_ip():
    """获取用户IP地址"""
    return request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')

def get_user_agent():
    """获取用户代理信息"""
    return request.headers.get('User-Agent', 'unknown')
