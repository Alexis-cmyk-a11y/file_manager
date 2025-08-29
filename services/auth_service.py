"""
用户认证服务
提供用户注册、登录、验证码等功能
"""

import os
import re
import time
import hashlib
import secrets
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import bcrypt

from services.redis_service import get_redis_service
from services.mysql_service import get_mysql_service
from services.email_service import get_email_service
from utils.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    """用户认证服务类"""
    
    def __init__(self):
        self.redis_service = get_redis_service()
        self.mysql_service = get_mysql_service()
        self.email_service = get_email_service()
        
        # 验证码配置
        self.verification_code_length = 6
        self.verification_code_expire = 300  # 5分钟
        self.verification_code_cooldown = 180  # 3分钟防刷
        
        # 安全配置
        self.max_login_attempts = 5
        self.ip_lockout_duration = 3600  # 1小时
        self.inactive_login_threshold = 180  # 180天
        
    def validate_email_format(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """验证密码强度"""
        if len(password) < 9:
            return False, "密码长度至少需要9位"
        
        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含大写字母"
        
        if not re.search(r'[a-z]', password):
            return False, "密码必须包含小写字母"
        
        if not re.search(r'\d', password):
            return False, "密码必须包含数字"
        
        return True, "密码强度符合要求"
    
    def generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return str(secrets.randbelow(900000) + 100000)
    
    def _get_verification_key(self, email: str, purpose: str) -> str:
        """获取验证码缓存键"""
        return f"verification:{purpose}:{email}"
    
    def _get_cooldown_key(self, email: str, purpose: str) -> str:
        """获取防刷限制键"""
        return f"cooldown:{purpose}:{email}"
    
    def _get_login_attempts_key(self, ip: str) -> str:
        """获取登录尝试次数键"""
        return f"login_attempts:{ip}"
    
    def _get_ip_lockout_key(self, ip: str) -> str:
        """获取IP锁定状态键"""
        return f"ip_lockout:{ip}"
    
    def send_verification_code(self, email: str, purpose: str = "register") -> Tuple[bool, str]:
        """发送验证码"""
        try:
            # 验证邮箱格式
            if not self.validate_email_format(email):
                return False, "邮箱格式不正确"
            
            # 检查防刷机制
            cooldown_key = self._get_cooldown_key(email, purpose)
            if self.redis_service.exists(cooldown_key):
                remaining_time = self.redis_service.ttl(cooldown_key)
                return False, f"请求过于频繁，请等待{remaining_time}秒后重试"
            
            # 生成验证码
            verification_code = self.generate_verification_code()
            
            # 存储验证码到缓存
            verification_key = self._get_verification_key(email, purpose)
            self.redis_service.setex(
                verification_key, 
                self.verification_code_expire, 
                verification_code
            )
            
            # 设置防刷限制
            self.redis_service.setex(
                cooldown_key, 
                self.verification_code_cooldown, 
                "1"
            )
            
            # 发送邮件
            if purpose == "register":
                subject = "注册验证码"
                template_data = {"email_verification_code": verification_code}
            else:
                subject = "登录验证码"
                template_data = {"email_verification_code": verification_code}
            
            success = self.email_service.send_email(
                to_email=email,
                subject=subject,
                template_data=template_data
            )
            
            if success:
                logger.info(f"验证码发送成功: {email}, 用途: {purpose}")
                return True, "验证码发送成功"
            else:
                # 发送失败，清理缓存
                self.redis_service.delete(verification_key)
                self.redis_service.delete(cooldown_key)
                return False, "验证码发送失败，请稍后重试"
                
        except Exception as e:
            logger.error(f"发送验证码失败: {e}")
            return False, "系统错误，请稍后重试"
    
    def verify_code(self, email: str, code: str, purpose: str = "register") -> Tuple[bool, str]:
        """验证验证码"""
        try:
            # 验证码格式检查
            if not re.match(r'^\d{6}$', code):
                return False, "验证码格式不正确"
            
            # 从缓存获取验证码
            verification_key = self._get_verification_key(email, purpose)
            stored_code = self.redis_service.get(verification_key)
            
            if not stored_code:
                return False, "验证码已过期或不存在"
            
            # 验证码匹配检查
            logger.info(f"验证码比较: stored_code='{stored_code}' (类型: {type(stored_code)}), code='{code}' (类型: {type(code)})")
            if stored_code != code:
                logger.warning(f"验证码不匹配: stored_code='{stored_code}' != code='{code}'")
                return False, "验证码错误"
            
            # 验证成功后立即删除验证码（即焚机制）
            self.redis_service.delete(verification_key)
            
            logger.info(f"验证码验证成功: {email}, 用途: {purpose}")
            return True, "验证码验证成功"
            
        except Exception as e:
            logger.error(f"验证码验证失败: {e}")
            return False, "系统错误，请稍后重试"
    
    def register_user(self, email: str, password: str, verification_code: str) -> Tuple[bool, str]:
        """用户注册"""
        try:
            # 验证邮箱格式
            if not self.validate_email_format(email):
                return False, "邮箱格式不正确"
            
            # 验证密码强度
            is_valid, password_msg = self.validate_password_strength(password)
            if not is_valid:
                return False, password_msg
            
            # 验证验证码
            is_valid, code_msg = self.verify_code(email, verification_code, "register")
            if not is_valid:
                return False, code_msg
            
            # 检查邮箱是否已注册
            if self.mysql_service.user_exists(email):
                return False, "该邮箱已被注册"
            
            # 密码加密
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            # 创建用户
            user_data = {
                'email': email,
                'password_hash': hashed_password.decode('utf-8'),
                'created_at': datetime.now(),
                'last_login': None,
                'status': 'active'
            }
            
            user_id = self.mysql_service.create_user(user_data)
            if user_id:
                # 为新用户创建个人空间
                self._setup_new_user_space(user_id, email)
                
                logger.info(f"用户注册成功: {email}, 用户ID: {user_id}")
                return True, "注册成功"
            else:
                return False, "注册失败，请稍后重试"
                
        except Exception as e:
            logger.error(f"用户注册失败: {e}")
            return False, "系统错误，请稍后重试"
    
    def _setup_new_user_space(self, user_id: int, email: str) -> None:
        """为新用户创建个人空间"""
        try:
            # 创建用户个人空间
            username = email.split('@')[0]
            success = self._create_user_personal_space(user_id, username)
            if success:
                logger.info(f"新用户 {email} 个人空间创建成功")
            else:
                logger.warning(f"新用户 {email} 个人空间创建失败")
                
        except Exception as e:
            logger.error(f"为新用户 {email} 创建个人空间失败: {e}")
            # 不抛出异常，避免影响用户注册流程
    
    def check_ip_lockout(self, ip: str) -> Tuple[bool, str]:
        """检查IP是否被锁定"""
        try:
            lockout_key = self._get_ip_lockout_key(ip)
            if self.redis_service.exists(lockout_key):
                remaining_time = self.redis_service.ttl(lockout_key)
                return True, f"IP地址已被锁定，请等待{remaining_time}秒后重试"
            return False, ""
        except Exception as e:
            logger.error(f"检查IP锁定状态失败: {e}")
            return False, ""
    
    def record_login_attempt(self, ip: str, success: bool) -> None:
        """记录登录尝试"""
        try:
            if success:
                # 登录成功，重置失败计数
                attempts_key = self._get_login_attempts_key(ip)
                self.redis_service.delete(attempts_key)
            else:
                # 登录失败，增加失败计数
                attempts_key = self._get_login_attempts_key(ip)
                attempts = self.redis_service.incr(attempts_key)
                
                # 设置过期时间
                if attempts == 1:
                    self.redis_service.expire(attempts_key, 3600)  # 1小时
                
                # 达到最大尝试次数，锁定IP
                if attempts >= self.max_login_attempts:
                    lockout_key = self._get_ip_lockout_key(ip)
                    self.redis_service.setex(lockout_key, self.ip_lockout_duration, "1")
                    logger.warning(f"IP地址 {ip} 因多次登录失败被锁定")
                    
        except Exception as e:
            logger.error(f"记录登录尝试失败: {e}")
    
    def check_inactive_login(self, email: str) -> bool:
        """检查是否需要验证码登录"""
        try:
            user = self.mysql_service.get_user_by_email(email)
            if not user:
                return False
            
            # 管理员账户不需要验证码验证
            if user.get('role') == 'admin':
                return False
            
            last_login = user.get('last_login')
            if not last_login:
                # 新用户第一次登录不需要验证码
                return False
            
            # 检查是否超过180天未登录
            days_since_login = (datetime.now() - last_login).days
            return days_since_login > self.inactive_login_threshold
            
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def login_user(self, email: str, password: str, ip: str, verification_code: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """用户登录"""
        try:
            # 检查IP锁定状态
            is_locked, lockout_msg = self.check_ip_lockout(ip)
            if is_locked:
                return False, lockout_msg, {}
            
            # 查找用户
            user = self.mysql_service.get_user_by_email(email)
            if not user:
                self.record_login_attempt(ip, False)
                return False, "邮箱或密码错误", {}
            
            # 检查账户状态
            if user.get('status') != 'active':
                return False, "账户已被禁用", {}
            
            # 检查是否需要验证码
            need_verification = self.check_inactive_login(email)
            if need_verification:
                if not verification_code:
                    return False, "需要验证码验证", {"need_verification": True}
                
                # 验证登录验证码
                is_valid, code_msg = self.verify_code(email, verification_code, "login")
                if not is_valid:
                    return False, code_msg, {"need_verification": True}
            
            # 验证密码
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                self.record_login_attempt(ip, False)
                return False, "邮箱或密码错误", {}
            
            # 登录成功
            self.record_login_attempt(ip, True)
            
            # 更新最后登录时间
            self.mysql_service.update_user_last_login(user['id'])
            
            # 生成登录凭证
            session_data = {
                'user_id': user['id'],
                'email': user['email'],
                'login_time': datetime.now().isoformat(),
                'ip_address': ip
            }
            
            logger.info(f"用户登录成功: {email}, IP: {ip}")
            return True, "登录成功", session_data
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return False, "系统错误，请稍后重试", {}
    
    def create_admin_user(self) -> bool:
        """创建管理员账户"""
        try:
            admin_email = "admin@system.local"
            admin_password = "Asdasd123"
            
            # 检查是否已存在
            if self.mysql_service.user_exists(admin_email):
                logger.info("管理员账户已存在")
                return True
            
            # 验证密码强度
            is_valid, _ = self.validate_password_strength(admin_password)
            if not is_valid:
                logger.error("管理员密码不符合强度要求")
                return False
            
            # 密码加密
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
            
            # 创建管理员用户
            admin_data = {
                'email': admin_email,
                'password_hash': hashed_password.decode('utf-8'),
                'created_at': datetime.now(),
                'last_login': None,
                'status': 'active',
                'role': 'admin'
            }
            
            user_id = self.mysql_service.create_user(admin_data)
            if user_id:
                logger.info(f"管理员账户创建成功: {admin_email}, 用户ID: {user_id}")
                return True
            else:
                logger.error("管理员账户创建失败")
                return False
                
        except Exception as e:
            logger.error(f"创建管理员账户失败: {e}")
            return False

    def _create_user_personal_space(self, user_id: int, username: str) -> bool:
        """创建用户个人空间"""
        try:
            import os
            
            # 创建用户目录
            user_dir = os.path.join('home', 'users', username)
            shared_dir = os.path.join('home', 'shared', f'{username}_shared')
            
            # 确保目录存在
            os.makedirs(user_dir, exist_ok=True)
            os.makedirs(shared_dir, exist_ok=True)
            
            # 设置目录权限（只读共享目录）
            os.chmod(shared_dir, 0o755)
            
            # 在数据库中记录用户空间
            mysql_service = get_mysql_service()
            sql = """
            INSERT INTO user_spaces (user_id, username, space_path) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE space_path = VALUES(space_path)
            """
            mysql_service.execute_update(sql, (user_id, username, user_dir))
            
            logger.info(f"用户 {username} 个人空间创建成功: {user_dir}")
            return True
            
        except Exception as e:
            logger.error(f"创建用户 {username} 个人空间失败: {e}")
            return False

# 全局实例
_auth_service = None

def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
