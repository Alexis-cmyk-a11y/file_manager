#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证系统初始化脚本
检查配置文件、创建管理员账户等
"""

import os
import sys
import secrets

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.auth_service import get_auth_service
from services.email_service import get_email_service
from utils.logger import get_logger

logger = get_logger('setup_auth')

def generate_secret_key():
    """生成安全的密钥"""
    return secrets.token_hex(32)

def setup_config_files():
    """设置配置文件"""
    print("📁 检查配置文件...")
    
    # 检查腾讯云配置文件
    tencent_config = os.path.join(project_root, 'config', 'tencent_cloud.py')
    if os.path.exists(tencent_config):
        print("✅ 腾讯云配置文件已存在")
    else:
        print("❌ 腾讯云配置文件不存在")
        print("💡 请复制 config/tencent_cloud.template.py 为 tencent_cloud.py 并配置您的密钥")
    
    # 检查主配置文件
    main_config = os.path.join(project_root, 'config.yaml')
    if os.path.exists(main_config):
        print("✅ 主配置文件已存在")
    else:
        print("❌ 主配置文件不存在")
    
    print("📋 配置文件检查完成")

def test_email_service():
    """测试邮件服务"""
    print("\n📧 测试邮件服务...")
    
    try:
        email_service = get_email_service()
        
        if not email_service.available:
            print("❌ 邮件服务不可用")
            print("💡 请检查以下配置：")
            print("   1. 确保 config/tencent_cloud.py 文件存在")
            print("   2. 检查腾讯云AKSK是否正确")
            print("   3. 确保配置文件中的密钥信息正确")
            return False
        
        print(f"   📮 发件邮箱: {email_service.from_email}")
        print(f"   🌍 服务区域: {email_service.region}")
        print(f"   🆔 模板ID: {email_service.template_id}")
        
        # 测试连接
        print("   🔗 测试连接...")
        success = email_service.test_connection()
        if success:
            print("✅ 邮件服务连接正常")
            return True
        else:
            print("❌ 邮件服务连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试邮件服务失败: {e}")
        return False

def create_admin_user():
    """创建管理员账户"""
    print("\n👤 创建管理员账户...")
    
    try:
        auth_service = get_auth_service()
        success = auth_service.create_admin_user()
        
        if success:
            print("✅ 管理员账户创建/检查完成")
            print("📧 邮箱: admin@system.local")
            print("🔑 密码: Asdasd123")
            print("⚠️  请及时修改默认密码")
            return True
        else:
            print("❌ 管理员账户创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 创建管理员账户失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 文件管理系统认证系统初始化")
    print("=" * 50)
    
    # 检查配置文件
    setup_config_files()
    
    # 测试邮件服务
    email_ok = test_email_service()
    
    # 创建管理员账户
    admin_ok = create_admin_user()
    
    print("\n" + "=" * 50)
    print("📋 初始化结果总结:")
    print(f"   配置文件: ✅ 完成")
    print(f"   邮件服务: {'✅ 正常' if email_ok else '❌ 异常'}")
    print(f"   管理员账户: {'✅ 完成' if admin_ok else '❌ 失败'}")
    
    if not email_ok:
        print("\n⚠️  邮件服务配置说明:")
        print("   1. 请确保 config/tencent_cloud.py 文件存在且配置正确")
        print("   2. 这些密钥可在腾讯云控制台获取: https://console.cloud.tencent.com/cam/capi")
        print("   3. 邮件服务用于发送验证码，如不需要可跳过")
    
    if admin_ok:
        print("\n🎉 认证系统初始化完成！")
        print("   现在可以启动系统并访问:")
        print("   - 登录页面: http://localhost:5000/login")
        print("   - 注册页面: http://localhost:5000/register")
    else:
        print("\n❌ 认证系统初始化失败，请检查错误信息")

if __name__ == '__main__':
    main()
