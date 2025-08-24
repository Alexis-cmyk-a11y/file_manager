"""
文件操作服务
提供文件系统操作的核心业务逻辑
"""

import os
import shutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from core.config import Config
from services.cache_service import get_cache_service
from services.mysql_service import get_mysql_service
from utils.logger import get_logger
from utils.file_utils import (
    FileUtils
)

logger = get_logger(__name__)

class FileService:
    """文件服务类"""
    
    def __init__(self):
        self.config = Config()
        self.cache_service = get_cache_service()
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
            # 转换字段名以匹配数据库期望的格式
            db_file_info = {
                'file_path': file_info.get('path'),  # 从 'path' 转换为 'file_path'
                'file_name': file_info.get('name'),  # 从 'name' 转换为 'file_name'
                'file_size': file_info.get('size', 0),
                'file_type': file_info.get('file_type'),
                'mime_type': file_info.get('mime_type'),
                'hash_value': file_info.get('hash_value'),
                'is_directory': file_info.get('is_directory', False),
                'parent_path': os.path.dirname(file_info.get('path', '')),
                'permissions': file_info.get('permissions'),
                'owner': 'system',  # 默认所有者
                'group_name': 'system'  # 默认组
            }
            
            # 验证必要字段
            if not db_file_info['file_path']:
                raise ValueError(f"文件路径不能为空: {file_info}")
            
            self.mysql_service.save_file_info(db_file_info)
        except Exception as e:
            logger.error(f"保存文件信息到数据库失败: {e}")
            # 重新抛出异常以便调试
            raise
    
    def _delete_file_info_from_db(self, file_path: str):
        """从数据库删除文件信息"""
        if not self.mysql_service or not self.mysql_service.is_connected():
            return
        
        try:
            self.mysql_service.delete_file_info(file_path)
        except Exception as e:
            logger.error(f"从数据库删除文件信息失败: {e}")
            # 重新抛出异常以便调试
            raise
    
    def list_directory(self, directory_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """列出目录内容"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(directory_path):
                raise ValueError("不安全的路径")
            
            # 处理空路径或"."，转换为当前工作目录
            if directory_path == "" or directory_path == ".":
                directory_path = "."
                actual_path = os.getcwd()
            else:
                actual_path = directory_path
            
            # 获取目录内容
            items = []
            total_size = 0
            file_count = 0
            dir_count = 0
            
            try:
                for item in os.listdir(actual_path):
                    item_path = os.path.join(actual_path, item)
                    item_info = FileUtils.get_file_info(item_path)
                    
                    if item_info:
                        items.append(item_info)
                        if item_info['is_directory']:
                            dir_count += 1
                        else:
                            file_count += 1
                            total_size += item_info['size']
            except PermissionError:
                raise PermissionError("没有权限访问该目录")
            
            # 按类型和名称排序
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            result = {
                'path': directory_path,
                'items': items,
                'total_items': len(items),
                'file_count': file_count,
                'dir_count': dir_count,
                'total_size': total_size,
                'formatted_size': FileUtils.format_file_size(total_size)
            }
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='list_directory',
                file_path=directory_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return result
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='list_directory',
                file_path=directory_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def get_file_info(self, file_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """获取文件信息"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                raise ValueError("不安全的路径")
            
            # 获取文件信息
            file_info = FileUtils.get_file_info(file_path)
            if not file_info:
                raise FileNotFoundError("文件不存在")
            
            # 保存文件信息到数据库
            self._save_file_info_to_db(file_path, file_info)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='get_file_info',
                file_path=file_path,
                file_name=file_info['name'],
                file_size=file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return file_info
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='get_file_info',
                file_path=file_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def create_directory(self, directory_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """创建目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(directory_path):
                raise ValueError("不安全的路径")
            
            # 检查目录是否已存在
            if os.path.exists(directory_path):
                raise FileExistsError("目录已存在")
            
            # 创建目录
            os.makedirs(directory_path, exist_ok=True)
            
            # 获取新创建的目录信息
            dir_info = FileUtils.get_file_info(directory_path)
            
            # 保存目录信息到数据库
            self._save_file_info_to_db(directory_path, dir_info)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='create_folder',
                file_path=directory_path,
                file_name=dir_info['name'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '目录创建成功',
                'directory': dir_info
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='create_folder',
                file_path=directory_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def delete_file(self, file_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """删除文件或目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                raise ValueError("不安全的路径")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError("文件不存在")
            
            # 获取文件信息（用于日志记录）
            file_info = FileUtils.get_file_info(file_path)
            
            # 删除文件或目录
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
                operation_type = 'delete_folder'
            else:
                os.remove(file_path)
                operation_type = 'delete'
            
            # 从数据库删除文件信息
            self._delete_file_info_from_db(file_path)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type=operation_type,
                file_path=file_path,
                file_name=file_info['name'] if file_info else None,
                file_size=file_info['size'] if file_info else None,
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '删除成功',
                'deleted_path': file_path
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='delete',
                file_path=file_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def rename_file(self, old_path: str, new_name: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """重命名文件或目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(old_path):
                raise ValueError("不安全的路径")
            
            if not FileUtils.is_safe_path(new_name):
                raise ValueError("新名称包含不安全字符")
            
            # 检查源文件是否存在
            if not os.path.exists(old_path):
                raise FileNotFoundError("源文件不存在")
            
            # 构建新路径
            parent_dir = os.path.dirname(old_path)
            new_path = os.path.join(parent_dir, new_name)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path):
                raise FileExistsError("目标文件已存在")
            
            # 获取原文件信息
            old_file_info = FileUtils.get_file_info(old_path)
            
            # 重命名文件
            os.rename(old_path, new_path)
            
            # 获取新文件信息
            new_file_info = FileUtils.get_file_info(new_path)
            
            # 更新数据库中的文件信息
            if self.mysql_service and self.mysql_service.is_connected():
                try:
                    # 删除旧记录
                    self._delete_file_info_from_db(old_path)
                    # 添加新记录
                    self._save_file_info_to_db(new_path, new_file_info)
                except Exception as db_error:
                    logger.warning(f"更新数据库文件信息失败: {db_error}")
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='rename',
                file_path=new_path,
                file_name=new_file_info['name'],
                file_size=new_file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '重命名成功',
                'old_path': old_path,
                'new_path': new_path,
                'file_info': new_file_info
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='rename',
                file_path=old_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def move_file(self, source_path: str, target_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """移动文件或目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(source_path):
                raise ValueError("源路径不安全")
            
            if not FileUtils.is_safe_path(target_path):
                raise ValueError("目标路径不安全")
            
            # 检查源文件是否存在
            if not os.path.exists(source_path):
                raise FileNotFoundError("源文件不存在")
            
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                raise FileExistsError("目标路径已存在")
            
            # 获取源文件信息
            source_file_info = FileUtils.get_file_info(source_path)
            
            # 移动文件
            shutil.move(source_path, target_path)
            
            # 获取移动后的文件信息
            target_file_info = FileUtils.get_file_info(target_path)
            
            # 更新数据库中的文件信息
            if self.mysql_service and self.mysql_service.is_connected():
                try:
                    # 删除旧记录
                    self._delete_file_info_from_db(source_path)
                    # 添加新记录
                    self._save_file_info_to_db(target_path, target_file_info)
                except Exception as db_error:
                    logger.warning(f"更新数据库文件信息失败: {db_error}")
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='move',
                file_path=target_path,
                file_name=target_file_info['name'],
                file_size=target_file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '移动成功',
                'source_path': source_path,
                'target_path': target_path,
                'file_info': target_file_info
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='move',
                file_path=source_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def copy_file(self, source_path: str, target_path: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """复制文件或目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(source_path):
                raise ValueError("源路径不安全")
            
            if not FileUtils.is_safe_path(target_path):
                raise ValueError("目标路径不安全")
            
            # 检查源文件是否存在
            if not os.path.exists(source_path):
                raise FileNotFoundError("源文件不存在")
            
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                raise FileExistsError("目标路径已存在")
            
            # 获取源文件信息
            source_file_info = FileUtils.get_file_info(source_path)
            
            # 复制文件
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
            
            # 获取复制后的文件信息
            target_file_info = FileUtils.get_file_info(target_path)
            
            # 保存新文件信息到数据库
            self._save_file_info_to_db(target_path, target_file_info)
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='copy',
                file_path=target_path,
                file_name=target_file_info['name'],
                file_size=target_file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'success': True,
                'message': '复制成功',
                'source_path': source_path,
                'target_path': target_path,
                'file_info': target_file_info
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='copy',
                file_path=source_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
    
    def search_files(self, search_path: str, query: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """搜索文件"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(search_path):
                raise ValueError("搜索路径不安全")
            
            if not query or len(query.strip()) == 0:
                raise ValueError("搜索查询不能为空")
            
            # 执行搜索
            results = []
            query_lower = query.lower()
            
            for root, dirs, files in os.walk(search_path):
                # 搜索目录
                for dir_name in dirs:
                    if query_lower in dir_name.lower():
                        dir_path = os.path.join(root, dir_name)
                        dir_info = FileUtils.get_file_info(dir_path)
                        if dir_info:
                            results.append(dir_info)
                
                # 搜索文件
                for file_name in files:
                    if query_lower in file_name.lower():
                        file_path = os.path.join(root, file_name)
                        file_info = FileUtils.get_file_info(file_path)
                        if file_info:
                            results.append(file_info)
            
            # 按类型和名称排序
            results.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='search',
                file_path=search_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            return {
                'search_path': search_path,
                'query': query,
                'results': results,
                'total_results': len(results)
            }
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='search',
                file_path=search_path,
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            raise
