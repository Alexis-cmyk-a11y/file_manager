"""
用户认证API路由
提供注册、登录、验证码等接口
"""

from flask import Blueprint, request, jsonify, session
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from datetime import datetime

from services.auth_service import get_auth_service
from utils.logger import get_logger

logger = get_logger(__name__)

# 创建蓝图
bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# 创建限流器
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@bp.route('/send-code', methods=['POST'])
@limiter.limit("5 per 3 minutes")  # 3分钟内最多5次
def send_verification_code():
    """发送验证码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        email = data.get('email', '').strip()
        purpose = data.get('purpose', 'register')  # register 或 login
        
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        if purpose not in ['register', 'login']:
            return jsonify({'success': False, 'message': '无效的验证码用途'}), 400
        
        # 获取认证服务
        auth_service = get_auth_service()
        
        # 发送验证码
        success, message = auth_service.send_verification_code(email, purpose)
        
        if success:
            return jsonify({
                'success': True, 
                'message': message,
                'data': {
                    'email': email,
                    'purpose': purpose,
                    'cooldown': 180  # 3分钟防刷
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"发送验证码接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/register', methods=['POST'])
@limiter.limit("10 per hour")  # 每小时最多10次注册
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        verification_code = data.get('verification_code', '').strip()
        
        # 参数验证
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        if not password:
            return jsonify({'success': False, 'message': '密码不能为空'}), 400
        
        if not verification_code:
            return jsonify({'success': False, 'message': '验证码不能为空'}), 400
        
        # 获取认证服务
        auth_service = get_auth_service()
        
        # 用户注册
        success, message = auth_service.register_user(email, password, verification_code)
        
        if success:
            logger.info(f"用户注册成功: {email}")
            return jsonify({
                'success': True, 
                'message': message,
                'data': {
                    'email': email,
                    'registered_at': datetime.now().isoformat()
                }
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"用户注册接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/login', methods=['POST'])
@limiter.limit("20 per hour")  # 每小时最多20次登录
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据不能为空'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        verification_code = data.get('verification_code', '').strip()
        
        # 参数验证
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'}), 400
        
        if not password:
            return jsonify({'success': False, 'message': '密码不能为空'}), 400
        
        # 获取客户端IP
        client_ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
        
        # 获取认证服务
        auth_service = get_auth_service()
        
        # 用户登录
        success, message, session_data = auth_service.login_user(
            email, password, client_ip, verification_code
        )
        
        if success:
            # 登录成功，设置session
            session['user_id'] = session_data['user_id']
            session['email'] = session_data['email']
            session['login_time'] = session_data['login_time']
            session['ip_address'] = session_data['ip_address']
            
            logger.info(f"用户登录成功: {email}, IP: {client_ip}")
            return jsonify({
                'success': True, 
                'message': message,
                'data': {
                    'user_id': session_data['user_id'],
                    'email': session_data['email'],
                    'login_time': session_data['login_time']
                }
            })
        else:
            # 检查是否需要验证码
            if message == "需要验证码验证":
                return jsonify({
                    'success': False, 
                    'message': message,
                    'need_verification': True
                }), 400
            else:
                return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"用户登录接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    try:
        # 清除session
        session.clear()
        
        logger.info("用户登出成功")
        return jsonify({
            'success': True, 
            'message': '登出成功'
        })
        
    except Exception as e:
        logger.error(f"用户登出接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        # 检查用户是否已登录
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '用户未登录'}), 401
        
        user_id = session['user_id']
        email = session['email']
        
        # 获取认证服务
        auth_service = get_auth_service()
        
        # 获取用户详细信息
        user = auth_service.mysql_service.get_user_by_id(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 返回用户信息（不包含敏感信息）
        profile_data = {
            'id': user['id'],
            'email': user['email'],
            'created_at': user['created_at'].isoformat() if user['created_at'] else None,
            'last_login': user['last_login'].isoformat() if user['last_login'] else None,
            'status': user['status'],
            'role': user.get('role', 'user')
        }
        
        return jsonify({
            'success': True, 
            'data': profile_data
        })
        
    except Exception as e:
        logger.error(f"获取用户信息接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/check-auth', methods=['GET'])
def check_auth():
    """检查用户认证状态"""
    try:
        if 'user_id' in session:
            return jsonify({
                'success': True, 
                'authenticated': True,
                'data': {
                    'user_id': session['user_id'],
                    'email': session['email'],
                    'login_time': session['login_time']
                }
            })
        else:
            return jsonify({
                'success': True, 
                'authenticated': False
            })
            
    except Exception as e:
        logger.error(f"检查认证状态接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500

@bp.route('/test-email', methods=['POST'])
def test_email():
    """测试邮件服务"""
    try:
        # 检查用户是否已登录且为管理员
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': '用户未登录'}), 401
        
        user_id = session['user_id']
        auth_service = get_auth_service()
        
        # 检查用户角色
        user = auth_service.mysql_service.get_user_by_id(user_id)
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': '权限不足'}), 403
        
        # 测试邮件服务
        email_service = auth_service.email_service
        success = email_service.test_connection()
        
        if success:
            return jsonify({
                'success': True, 
                'message': '邮件服务连接正常'
            })
        else:
            return jsonify({
                'success': False, 
                'message': '邮件服务连接失败'
            }), 500
            
    except Exception as e:
        logger.error(f"测试邮件服务接口错误: {e}")
        return jsonify({'success': False, 'message': '系统错误，请稍后重试'}), 500
