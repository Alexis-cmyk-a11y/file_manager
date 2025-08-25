# 腾讯云配置模板文件
# 使用方法：
# 1. 复制此文件为 tencent_cloud.py
# 2. 修改以下配置项为您的实际值
# 3. 确保 tencent_cloud.py 已添加到 .gitignore 中

# 腾讯云API密钥
TENCENTCLOUD_SECRET_ID = "your-tencentcloud-secret-id"
TENCENTCLOUD_SECRET_KEY = "your-tencentcloud-secret-key"

# 腾讯云SES邮件服务配置
SES_REGION = "ap-guangzhou"
SES_FROM_EMAIL = "your-email@your-domain.com"
SES_TEMPLATE_ID = 12345

# 配置说明
# 1. TENCENTCLOUD_SECRET_ID: 腾讯云API密钥ID，从腾讯云控制台获取
# 2. TENCENTCLOUD_SECRET_KEY: 腾讯云API密钥Key，从腾讯云控制台获取
# 3. SES_REGION: 腾讯云SES服务区域，默认为广州
# 4. SES_FROM_EMAIL: 发件人邮箱地址，需要在腾讯云SES中验证
# 5. SES_TEMPLATE_ID: 邮件模板ID，需要在腾讯云SES中创建模板

# 安全提醒
# - 请妥善保管您的API密钥，不要将其提交到版本控制系统
# - 建议将此文件添加到 .gitignore 中
# - 生产环境请使用更安全的密钥管理方式
