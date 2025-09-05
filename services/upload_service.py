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
from services.cache_service import get_cache_service
from utils.logger import get_logger
from utils.file_utils import FileUtils

logger = get_logger(__name__)

class UploadService:
    """文件上传服务类"""
    
    def __init__(self):
        self.config = Config()
        self.mysql_service = None
        self.cache_service = get_cache_service()
        
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
    
    def _invalidate_cache(self, file_path: str, current_user: Dict[str, Any] = None) -> None:
        """清理相关缓存"""
        try:
            import hashlib
            
            # 获取用户ID
            user_id = current_user['user_id'] if current_user else 'anonymous'
            logger.info(f"开始清理上传缓存，文件路径: {file_path}, 用户ID: {user_id}")
            
            # 清理文件信息缓存
            file_cache_key = f"file_info:{user_id}:{hashlib.md5(file_path.encode()).hexdigest()[:16]}"
            self.cache_service.delete(file_cache_key)
            logger.info(f"清理文件信息缓存: {file_path} -> {file_cache_key}")
            
            # 清理父目录的目录列表缓存
            parent_dir = os.path.dirname(file_path) if file_path != '.' else '.'
            dir_cache_key = f"dir_listing:{user_id}:{hashlib.md5(parent_dir.encode()).hexdigest()[:16]}"
            self.cache_service.delete(dir_cache_key)
            logger.info(f"清理父目录缓存: {parent_dir} -> {dir_cache_key}")
            
            # 清理所有相关的目录列表缓存（使用模式匹配）
            pattern = "dir_listing:*"
            cleared_count = self.cache_service.clear_pattern(pattern)
            logger.info(f"清理目录列表缓存模式: {pattern}, 清理了 {cleared_count} 个键")
            
            logger.info(f"上传缓存清理完成，文件路径: {file_path}")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {file_path}, 错误: {e}")
    
    def upload_file(self, file, target_directory: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """上传单个文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(target_directory):
                raise ValueError("目标目录路径不安全")
            
            # 处理空路径，使用当前工作目录
            if not target_directory or target_directory == '':
                target_directory = '.'
            
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
            
            # 清理相关缓存
            self._invalidate_cache(target_path, current_user)
            
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
    
    def upload_multiple_files(self, files: List, target_directory: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """上传多个文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(target_directory):
                raise ValueError("目标目录路径不安全")
            
            # 处理空路径，使用当前工作目录
            if not target_directory or target_directory == '':
                target_directory = '.'
            
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
            
            # 清理相关缓存（清理目标目录的缓存）
            self._invalidate_cache(target_directory, current_user)
            
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
            
            # 移除文件扩展名检查，允许所有文件类型上传
            
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
