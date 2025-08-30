"""
用户认证API路由
包含登录、注册、邮箱验证等功能
"""

from flask import Blueprint, request, jsonify, session
from flask_limiter.util import get_remote_address

from services.auth_service import get_auth_service
from utils.logger import get_logger
from utils.auth_middleware import require_auth_api, get_current_user

logger = get_logger(__name__)
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': '邮箱和密码不能为空'
            }), 400
        
        # 获取用户IP
        user_ip = request.remote_addr
        
        # 调用认证服务
        auth_service = get_auth_service()
        success, message, session_data = auth_service.login_user(email, password, user_ip)
        
        if success:
            # 设置session
            session['user_id'] = session_data['user_id']
            session['email'] = session_data['email']
            session['login_time'] = session_data['login_time']
            session['ip_address'] = session_data['ip_address']
            
            logger.info(f"用户登录成功: {email}, IP: {user_ip}")
            
            return jsonify({
                'success': True,
                'message': message,
                'user': {
                    'email': email,
                    'login_time': session_data['login_time']
                }
            })
        else:
            logger.warning(f"用户登录失败: {email}, IP: {user_ip}, 原因: {message}")
            return jsonify({
                'success': False,
                'message': message
            }), 401
            
    except Exception as e:
        logger.error(f"登录处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        verification_code = data.get('verification_code')
        
        if not email or not password or not confirm_password or not verification_code:
            return jsonify({
                'success': False,
                'message': '所有字段都必须填写'
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': '两次输入的密码不一致'
            }), 400
        
        # 获取用户IP
        user_ip = request.remote_addr
        
        # 调用认证服务
        auth_service = get_auth_service()
        success, message = auth_service.register_user(email, password, verification_code)
        
        if success:
            logger.info(f"用户注册成功: {email}, IP: {user_ip}")
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            logger.warning(f"用户注册失败: {email}, IP: {user_ip}, 原因: {message}")
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"注册处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/logout', methods=['POST'])
@require_auth_api
def logout():
    """用户登出"""
    try:
        current_user = get_current_user()
        if current_user:
            logger.info(f"用户登出: {current_user['email']}")
        
        # 清除session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': '登出成功'
        })
        
    except Exception as e:
        logger.error(f"登出处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/user/info', methods=['GET'])
@require_auth_api
def get_user_info():
    """获取当前用户信息"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({
                'success': False,
                'message': '用户未登录'
            }), 401
        
        # 获取用户详细信息
        auth_service = get_auth_service()
        user_info = auth_service.get_user_info(current_user['user_id'])
        
        if user_info:
            return jsonify({
                'success': True,
                'user': user_info
            })
        else:
            return jsonify({
                'success': False,
                'message': '获取用户信息失败'
            }), 404
            
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/verify-email', methods=['POST'])
def verify_email():
    """邮箱验证"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        email = data.get('email')
        verification_code = data.get('verification_code')
        
        if not email or not verification_code:
            return jsonify({
                'success': False,
                'message': '邮箱和验证码不能为空'
            }), 400
        
        # 调用认证服务
        auth_service = get_auth_service()
        success, message = auth_service.verify_code(email, verification_code)
        
        if success:
            logger.info(f"邮箱验证成功: {email}")
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            logger.warning(f"邮箱验证失败: {email}, 原因: {message}")
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"邮箱验证处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/send-verification', methods=['POST'])
def send_verification():
    """发送邮箱验证码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'message': '邮箱不能为空'
            }), 400
        
        # 获取用户IP
        user_ip = request.remote_addr
        
        # 调用认证服务
        auth_service = get_auth_service()
        success, message = auth_service.send_verification_code(email, "register")
        
        if success:
            logger.info(f"验证码发送成功: {email}, IP: {user_ip}")
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            logger.warning(f"验证码发送失败: {email}, IP: {user_ip}, 原因: {message}")
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"发送验证码处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

@bp.route('/send-code', methods=['POST'])
def send_code():
    """发送验证码 (兼容前端调用)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        email = data.get('email')
        purpose = data.get('purpose', 'register')  # 默认为注册
        
        if not email:
            return jsonify({
                'success': False,
                'message': '邮箱不能为空'
            }), 400
        
        # 获取用户IP
        user_ip = request.remote_addr
        
        # 调用认证服务
        auth_service = get_auth_service()
        success, message = auth_service.send_verification_code(email, purpose)
        
        if success:
            logger.info(f"验证码发送成功: {email}, 用途: {purpose}, IP: {user_ip}")
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            logger.warning(f"验证码发送失败: {email}, 用途: {purpose}, IP: {user_ip}, 原因: {message}")
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"发送验证码处理失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500
