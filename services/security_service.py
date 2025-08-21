"""
安全服务
提供路径验证、文件类型验证等安全功能
"""

import os
import logging
from core.config import Config

logger = logging.getLogger(__name__)

class SecurityService:
    """安全服务类"""
    
    def __init__(self):
        self.config = Config()
    
    def validate_path_safety(self, path):
        """验证路径安全性"""
        # 空路径表示根目录，这是允许的
        if not path:
            return True, self.config.ROOT_DIR
        
        # 检查路径遍历攻击
        if '..' in path or path.startswith('/') or ':' in path:
            return False, "无效的路径"
        
        # 构建完整路径
        full_path = os.path.join(self.config.ROOT_DIR, path)
        
        # 检查是否在根目录范围内
        if not os.path.abspath(full_path).startswith(os.path.abspath(self.config.ROOT_DIR)):
            return False, "无法访问根目录之外的路径"
        
        return True, full_path
    
    def validate_file_extension(self, filename):
        """验证文件扩展名"""
        if not filename:
            return False, "文件名不能为空"
        
        # 检查禁止的文件类型
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in self.config.FORBIDDEN_EXTENSIONS:
            return False, f"不允许上传 {file_ext} 类型的文件"
        
        # 检查允许的文件类型（如果配置了的话）
        if hasattr(self.config, 'ALLOWED_EXTENSIONS') and self.config.ALLOWED_EXTENSIONS:
            if file_ext not in self.config.ALLOWED_EXTENSIONS:
                return False, f"只允许上传 {', '.join(self.config.ALLOWED_EXTENSIONS)} 类型的文件"
        
        return True, "文件类型验证通过"
    
    def validate_file_size(self, file_size):
        """验证文件大小"""
        if hasattr(self.config, 'MAX_FILE_SIZE'):
            if file_size > self.config.MAX_FILE_SIZE:
                return False, f"文件大小超过限制 ({file_size} > {self.config.MAX_FILE_SIZE})"
        return True, "文件大小验证通过"
