"""
上传服务
处理文件上传的业务逻辑
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename

from core.config import Config
from services.mysql_service import get_mysql_service
from utils.logger import get_logger
from utils.file_utils import FileUtils

logger = get_logger(__name__)

class UploadService:
    """文件上传服务类"""
    
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
    
    def _save_file_info_to_db(self, file_path: str, file_info: Dict[str, Any]):
        """保存文件信息到数据库"""
        if not self.mysql_service or not self.mysql_service.is_connected():
            return
        
        try:
            self.mysql_service.save_file_info(file_info)
        except Exception as e:
            logger.error(f"保存文件信息到数据库失败: {e}")
    
    def upload_file(self, file, target_directory: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """上传单个文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(target_directory):
                raise ValueError("目标目录路径不安全")
            
            # 检查目标目录是否存在
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
            
            # 获取安全的文件名
            filename = secure_filename(file.filename)
            if not filename:
                raise ValueError("无效的文件名")
            
            # 构建目标文件路径
            target_path = os.path.join(target_directory, filename)
            
            # 检查文件是否已存在
            if os.path.exists(target_path):
                raise FileExistsError("文件已存在")
            
            # 保存文件
            file.save(target_path)
            
            # 获取文件信息
            file_info = FileUtils.get_file_info(target_path)
            
            # 保存文件信息到数据库
            self._save_file_info_to_db(target_path, file_info)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='upload',
                file_path=target_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '文件上传成功',
                'file_info': file_info,
                'target_path': target_path
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='upload',
                file_path=target_directory,
                file_name=file.filename if file else None,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def upload_multiple_files(self, files: List, target_directory: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """上传多个文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(target_directory):
                raise ValueError("目标目录路径不安全")
            
            # 检查目标目录是否存在
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
            
            uploaded_files = []
            failed_files = []
            
            for file in files:
                try:
                    # 获取安全的文件名
                    filename = secure_filename(file.filename)
                    if not filename:
                        failed_files.append({
                            'filename': file.filename,
                            'error': '无效的文件名'
                        })
                        continue
                    
                    # 构建目标文件路径
                    target_path = os.path.join(target_directory, filename)
                    
                    # 检查文件是否已存在
                    if os.path.exists(target_path):
                        failed_files.append({
                            'filename': filename,
                            'error': '文件已存在'
                        })
                        continue
                    
                    # 保存文件
                    file.save(target_path)
                    
                    # 获取文件信息
                    file_info = FileUtils.get_file_info(target_path)
                    
                    # 保存文件信息到数据库
                    self._save_file_info_to_db(target_path, file_info)
                    
                    uploaded_files.append({
                        'filename': filename,
                        'file_info': file_info,
                        'target_path': target_path
                    })
                    
                except Exception as e:
                    failed_files.append({
                        'filename': file.filename,
                        'error': str(e)
                    })
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='upload',
                file_path=target_directory,
                user_ip=user_ip,
                user_agent=user_agent,
                status='success' if uploaded_files else 'failed',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': f'批量上传完成，成功: {len(uploaded_files)}, 失败: {len(failed_files)}',
                'uploaded_files': uploaded_files,
                'failed_files': failed_files,
                'total_files': len(files),
                'success_count': len(uploaded_files),
                'failed_count': len(failed_files)
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='upload',
                file_path=target_directory,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def validate_upload(self, file, max_size: int = None) -> Dict[str, Any]:
        """验证上传文件"""
        try:
            # 检查文件大小
            if max_size and file.content_length > max_size:
                return {
                    'valid': False,
                    'error': f'文件大小超过限制: {file.content_length} > {max_size}'
                }
            
            # 检查文件扩展名
            filename = file.filename.lower()
            forbidden_extensions = self.config.FORBIDDEN_EXTENSIONS
            
            for ext in forbidden_extensions:
                if filename.endswith(ext.lower()):
                    return {
                        'valid': False,
                        'error': f'不允许上传的文件类型: {ext}'
                    }
            
            return {
                'valid': True,
                'message': '文件验证通过'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'文件验证失败: {str(e)}'
            }
    
    def get_upload_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取上传统计信息"""
        if not self.mysql_service or not self.mysql_service.is_connected():
            return {
                'success': False,
                'message': 'MySQL服务不可用'
            }
        
        try:
            stats = self.mysql_service.get_operation_stats(days)
            return stats
        except Exception as e:
            logger.error(f"获取上传统计失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
