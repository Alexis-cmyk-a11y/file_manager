"""
下载服务
处理文件下载的业务逻辑
"""

import os

from core.config import Config
from services.security_service import SecurityService
from utils.logger import get_logger

logger = get_logger(__name__)

class DownloadService:
    """下载服务类"""
    
    def __init__(self):
        self.config = Config()
        self.security_service = SecurityService()
    
    def download_file(self, file_path):
        """下载指定文件"""
        # 检查是否启用下载功能
        if not self.config.ENABLE_DOWNLOAD:
            logger.warning("尝试下载文件，但下载功能已禁用")
            return {'success': False, 'message': '下载功能已禁用'}
        
        # 验证文件路径安全性
        is_safe, result = self.security_service.validate_path_safety(file_path)
        if not is_safe:
            logger.warning(f"下载文件路径安全检查失败: {file_path}")
            return {'success': False, 'message': result}
        
        full_path = result
        logger.info(f"尝试下载文件: {full_path}")
        
        # 检查文件是否存在
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            logger.warning(f"请求下载的文件不存在: {full_path}")
            return {'success': False, 'message': '文件不存在'}
        
        try:
            directory = os.path.dirname(full_path)
            filename = os.path.basename(full_path)
            file_size = os.path.getsize(full_path)
            logger.info(f"下载文件: {filename}, 大小: {file_size} 字节")
            
            return {
                'success': True,
                'directory': directory,
                'filename': filename,
                'file_size': file_size
            }
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return {'success': False, 'message': '文件下载失败，请稍后重试'}
