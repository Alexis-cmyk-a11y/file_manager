"""
下载服务
处理文件下载的业务逻辑
"""

import os
import time
from typing import Dict, Any, Optional, Tuple
from flask import send_file, Response, request

from core.config import Config
from services.mysql_service import get_mysql_service
from utils.logger import get_logger
from utils.file_utils import FileUtils

logger = get_logger(__name__)

class DownloadService:
    """文件下载服务类"""
    
    def __init__(self):
        self.config = Config()
        self.mysql_service = None
        
        # 尝试初始化MySQL服务
        try:
            self.mysql_service = get_mysql_service()
            if self.mysql_service and self.mysql_service.is_connected():
                logger.info("MySQL服务集成成功")
            else:
                logger.warning("MySQL服务不可用，将跳过数据库日志记录")
        except Exception as e:
            logger.warning(f"MySQL服务初始化失败: {e}")
    
    def _log_operation(self, operation_type: str, file_path: str = None, 
                       file_name: str = None, file_size: int = None, 
                       user_ip: str = None, user_agent: str = None,
                       status: str = 'success', error_message: str = None,
                       duration_ms: int = None):
        """记录文件操作到MySQL数据库"""
        if not self.mysql_service or not self.mysql_service.is_connected():
            return
        
        try:
            self.mysql_service.log_file_operation(
                operation_type=operation_type,
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                user_ip=user_ip,
                user_agent=user_agent,
                status=status,
                error_message=error_message,
                duration_ms=duration_ms
            )
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
    
    def download_file(self, file_path: str, user_ip: str = None, user_agent: str = None) -> Response:
        """下载文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                raise ValueError("文件路径不安全")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError("文件不存在")
            
            # 检查是否为文件
            if not os.path.isfile(file_path):
                raise ValueError("路径不是文件")
            
            # 获取文件信息
            file_info = FileUtils.get_file_info(file_path)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='download',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            # 发送文件 - 使用绝对路径确保正确解析
            abs_file_path = os.path.abspath(file_path)
            return send_file(
                abs_file_path,
                as_attachment=True,
                download_name=file_info['name']
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='download',
                file_path=file_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def download_directory_as_zip(self, directory_path: str, user_ip: str = None, user_agent: str = None) -> Response:
        """将目录打包为ZIP文件下载"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(directory_path):
                raise ValueError("目录路径不安全")
            
            # 检查目录是否存在
            if not os.path.exists(directory_path):
                raise FileNotFoundError("目录不存在")
            
            # 检查是否为目录
            if not os.path.isdir(directory_path):
                raise ValueError("路径不是目录")
            
            # 获取目录信息
            dir_info = FileUtils.get_file_info(directory_path)
            
            # 创建临时ZIP文件
            import tempfile
            import zipfile
            
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, f"{dir_info['name']}.zip")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, directory_path)
                        zipf.write(file_path, arcname)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='download',
                file_path=directory_path,
                file_name=f"{dir_info['name']}.zip",
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            # 发送ZIP文件
            response = send_file(
                zip_path,
                as_attachment=True,
                download_name=f"{dir_info['name']}.zip",
                mimetype='application/zip'
            )
            
            # 设置响应头，告诉浏览器这是ZIP文件
            response.headers['Content-Type'] = 'application/zip'
            
            return response
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='download',
                file_path=directory_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def get_download_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取下载统计信息"""
        if not self.mysql_service or not self.mysql_service.is_connected():
            return {
                'success': False,
                'message': 'MySQL服务不可用'
            }
        
        try:
            stats = self.mysql_service.get_operation_stats(days)
            return stats
        except Exception as e:
            logger.error(f"获取下载统计失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def validate_download_path(self, file_path: str) -> Dict[str, Any]:
        """验证下载路径"""
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                return {
                    'valid': False,
                    'error': '文件路径不安全'
                }
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'error': '文件不存在'
                }
            
            # 检查权限
            if not os.access(file_path, os.R_OK):
                return {
                    'valid': False,
                    'error': '没有读取权限'
                }
            
            return {
                'valid': True,
                'message': '路径验证通过'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'路径验证失败: {str(e)}'
            }
