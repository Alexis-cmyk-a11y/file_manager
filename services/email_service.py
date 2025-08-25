"""
邮件服务
使用腾讯云SES发送邮件
"""

import os
import json
from typing import Dict, Any, Optional
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.ses.v20201002 import ses_client, models

from utils.logger import get_logger

logger = get_logger(__name__)

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        # 优先从配置文件读取
        try:
            from config.tencent_cloud import (
                TENCENTCLOUD_SECRET_ID, 
                TENCENTCLOUD_SECRET_KEY, 
                SES_REGION, 
                SES_FROM_EMAIL, 
                SES_TEMPLATE_ID
            )
            self.secret_id = TENCENTCLOUD_SECRET_ID
            self.secret_key = TENCENTCLOUD_SECRET_KEY
            self.region = SES_REGION
            self.from_email = SES_FROM_EMAIL
            self.template_id = SES_TEMPLATE_ID
        except ImportError:
            # 如果配置文件不存在，使用默认值
            self.secret_id = "your-tencentcloud-secret-id"
            self.secret_key = "your-tencentcloud-secret-key"
            self.region = "ap-guangzhou"
            self.from_email = "system@fyle.com.cn"
            self.template_id = 35165
        
        # 检查配置
        if not self.secret_id or not self.secret_key:
            logger.warning("腾讯云SES配置缺失，邮件功能将不可用")
            self.available = False
        else:
            self.available = True
            self._initialize_client()
    
    def _initialize_client(self):
        """初始化腾讯云SES客户端"""
        try:
            # 创建认证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            
            # 配置HTTP选项
            http_profile = HttpProfile()
            http_profile.endpoint = "ses.tencentcloudapi.com"
            
            # 配置客户端选项
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            
            # 创建SES客户端
            self.client = ses_client.SesClient(cred, self.region, client_profile)
            
            logger.info("腾讯云SES客户端初始化成功")
            
        except Exception as e:
            logger.error(f"腾讯云SES客户端初始化失败: {e}")
            self.available = False
    
    def send_email(self, to_email: str, subject: str, template_data: Dict[str, Any]) -> bool:
        """发送邮件"""
        if not self.available:
            logger.error("邮件服务不可用")
            return False
        
        try:
            # 创建发送邮件请求
            req = models.SendEmailRequest()
            
            # 构建请求参数
            params = {
                "FromEmailAddress": self.from_email,
                "Destination": [to_email],
                "Subject": subject,
                "Template": {
                    "TemplateID": self.template_id,
                    "TemplateData": json.dumps(template_data)
                }
            }
            
            req.from_json_string(json.dumps(params))
            
            # 发送邮件
            resp = self.client.SendEmail(req)
            
            logger.info(f"邮件发送成功: {to_email}, 主题: {subject}")
            return True
            
        except TencentCloudSDKException as err:
            logger.error(f"腾讯云SES发送邮件失败: {err}")
            return False
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False
    
    def send_verification_code(self, to_email: str, code: str, purpose: str = "register") -> bool:
        """发送验证码邮件"""
        if purpose == "register":
            subject = "注册验证码"
        else:
            subject = "登录验证码"
        
        template_data = {
            "email_verification_code": code
        }
        
        return self.send_email(to_email, subject, template_data)
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """发送欢迎邮件"""
        subject = "欢迎加入文件管理系统"
        template_data = {
            "username": username,
            "welcome_message": "感谢您注册文件管理系统！"
        }
        
        return self.send_email(to_email, subject, template_data)
    
    def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """发送密码重置邮件"""
        subject = "密码重置验证码"
        template_data = {
            "email_verification_code": reset_code
        }
        
        return self.send_email(to_email, subject, template_data)
    
    def test_connection(self) -> bool:
        """测试邮件服务连接"""
        if not self.available:
            return False
        
        try:
            # 尝试发送测试邮件到系统邮箱
            test_data = {"email_verification_code": "123456"}
            return self.send_email(self.from_email, "连接测试", test_data)
        except Exception as e:
            logger.error(f"邮件服务连接测试失败: {e}")
            return False

# 全局实例
_email_service = None

def get_email_service() -> EmailService:
    """获取邮件服务实例"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
