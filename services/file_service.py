"""
文件操作服务
提供文件系统操作的核心业务逻辑
"""

import os
import shutil
import time
import hashlib
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
    
    def list_directory(self, directory_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """列出目录内容"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(directory_path):
                raise ValueError("不安全的路径")
            
            # 用户权限检查
            if current_user:
                from services.security_service import get_security_service
                security_service = get_security_service()
                
                # 清理和验证用户路径
                directory_path = security_service.sanitize_path_for_user(
                    current_user['user_id'], 
                    current_user['email'], 
                    directory_path
                )
            
            # 处理空路径或"."，使用配置的根目录
            if directory_path == "" or directory_path == ".":
                # 使用配置的根目录而不是当前工作目录
                actual_path = self.config.FILESYSTEM_ROOT
                directory_path = actual_path
            else:
                actual_path = directory_path
            
            # 生成包含用户信息的缓存键
            user_id = current_user['user_id'] if current_user else 'anonymous'
            cache_key = f"dir_listing:{user_id}:{hashlib.md5(directory_path.encode()).hexdigest()[:16]}"
            
            # 尝试从缓存获取
            cached_result = self.cache_service.get(cache_key)
            if cached_result:
                logger.info(f"✅ 缓存命中 - 目录列表: {directory_path}, 缓存键: {cache_key}")
                logger.info(f"缓存数据项目数量: {len(cached_result.get('items', []))}")
                # 更新最后访问时间
                cached_result['cached_at'] = time.time()
                return cached_result
            
            # 缓存未命中，从文件系统获取
            logger.info(f"❌ 缓存未命中 - 目录列表: {directory_path}, 缓存键: {cache_key}")
            
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
                raise PermissionError("目录访问被拒绝")
            
            # 按类型和名称排序
            items.sort(key=lambda x: (not x['is_directory'], x['name'].lower()))
            
            # 处理items中的datetime对象，转换为字符串
            processed_items = []
            for item in items:
                processed_item = item.copy()
                if 'created_time' in processed_item and hasattr(processed_item['created_time'], 'isoformat'):
                    processed_item['created_time'] = processed_item['created_time'].isoformat()
                if 'modified_time' in processed_item and hasattr(processed_item['modified_time'], 'isoformat'):
                    processed_item['modified_time'] = processed_item['modified_time'].isoformat()
                processed_items.append(processed_item)
            
            result = {
                'path': directory_path,
                'items': processed_items,
                'total_items': len(items),
                'file_count': file_count,
                'dir_count': dir_count,
                'total_size': total_size,
                'formatted_size': FileUtils.format_file_size(total_size),
                'cached_at': time.time()
            }
            
            # 缓存结果
            cache_success = self.cache_service.set(
                cache_key, 
                result, 
                data_type='dir_listing',
                data_size=len(items)
            )
            if cache_success:
                logger.info(f"💾 目录列表已缓存: {directory_path} (键: {cache_key})")
            else:
                logger.warning(f"⚠️ 目录列表缓存失败: {directory_path}")
            
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
    
    def get_file_info(self, file_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取文件信息"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                raise ValueError("不安全的路径")
            
            # 用户权限检查
            if current_user:
                from services.security_service import get_security_service
                security_service = get_security_service()
                
                # 检查用户是否有权限访问该文件
                directory_path = os.path.dirname(file_path) if file_path != '.' else '.'
                if not security_service.check_user_directory_access(
                    current_user['user_id'], 
                    current_user['email'], 
                    directory_path
                ):
                    raise PermissionError("没有权限访问该文件")
            
            # 生成包含用户信息的缓存键
            user_id = current_user['user_id'] if current_user else 'anonymous'
            cache_key = f"file_info:{user_id}:{hashlib.md5(file_path.encode()).hexdigest()[:16]}"
            
            # 尝试从缓存获取
            cached_file_info = self.cache_service.get(cache_key)
            if cached_file_info:
                logger.debug(f"从缓存获取文件信息: {file_path}")
                # 更新最后访问时间
                cached_file_info['cached_at'] = time.time()
                return cached_file_info
            
            # 缓存未命中，从文件系统获取
            logger.debug(f"缓存未命中，从文件系统获取文件信息: {file_path}")
            
            # 获取文件信息
            file_info = FileUtils.get_file_info(file_path)
            if not file_info:
                raise FileNotFoundError("文件不存在")
            
            # 添加缓存时间戳
            file_info['cached_at'] = time.time()
            
            # 缓存文件信息
            self.cache_service.set(
                cache_key, 
                file_info, 
                data_type='file_info'
            )
            logger.debug(f"文件信息已缓存: {file_path}")
            
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
    
    def create_directory(self, directory_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """创建目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(directory_path):
                raise ValueError("不安全的路径")
            
            # 用户权限检查
            if current_user:
                from services.security_service import get_security_service
                security_service = get_security_service()
                
                # 检查用户是否有权限在该目录创建文件夹
                parent_directory = os.path.dirname(directory_path) if directory_path != '.' else '.'
                if not security_service.check_user_directory_access(
                    current_user['user_id'], 
                    current_user['email'], 
                    parent_directory
                ):
                    raise PermissionError("没有权限在该目录创建文件夹")
            
            # 检查目录是否已存在
            if os.path.exists(directory_path):
                raise FileExistsError("目录已存在")
            
            # 创建目录
            os.makedirs(directory_path, exist_ok=True)
            
            # 获取新创建的目录信息
            dir_info = FileUtils.get_file_info(directory_path)
            
            # 保存目录信息到数据库
            self._save_file_info_to_db(directory_path, dir_info)
            
            # 清理父目录缓存
            parent_dir = os.path.dirname(directory_path) if directory_path != '.' else '.'
            self._invalidate_cache(parent_dir, current_user)
            
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
    
    def delete_file(self, file_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
        """删除文件或目录"""
        start_time = time.time()
        
        try:
            # 安全检查
            if not FileUtils.is_safe_path(file_path):
                raise ValueError("不安全的路径")
            
            # 用户权限检查
            if current_user:
                from services.security_service import get_security_service
                security_service = get_security_service()
                
                # 检查用户是否有权限删除该文件
                directory_path = os.path.dirname(file_path) if file_path != '.' else '.'
                if not security_service.check_user_directory_access(
                    current_user['user_id'], 
                    current_user['email'], 
                    directory_path
                ):
                    raise PermissionError("没有权限删除该文件")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.warning(f"文件不存在，无法删除: {file_path}")
                raise FileNotFoundError("文件不存在")
            
            logger.info(f"文件存在，准备删除: {file_path}")
            
            # 获取文件信息（用于日志记录）
            file_info = FileUtils.get_file_info(file_path)
            logger.info(f"文件信息: {file_info}")
            
            # 在删除源文件之前，检查并清理相关的共享文件
            self._cleanup_related_shares(file_path)
            
            # 删除文件或目录
            if os.path.isdir(file_path):
                logger.info(f"删除目录: {file_path}")
                shutil.rmtree(file_path)
                operation_type = 'delete_folder'
            else:
                logger.info(f"删除文件: {file_path}")
                os.remove(file_path)
                operation_type = 'delete'
            
            # 验证文件是否真的被删除
            if os.path.exists(file_path):
                logger.error(f"文件删除失败，文件仍然存在: {file_path}")
                raise Exception("文件删除失败")
            else:
                logger.info(f"文件删除成功，文件已不存在: {file_path}")
            
            # 从数据库删除文件信息
            self._delete_file_info_from_db(file_path)
            
            # 清理相关缓存（在文件删除后）
            self._invalidate_cache(file_path, current_user)
            
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
    
    def rename_file(self, old_path: str, new_name: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            # 清理相关缓存
            self._invalidate_cache(old_path, current_user)
            self._invalidate_cache(new_path, current_user)
            
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
    
    def move_file(self, source_path: str, target_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            # 清理相关缓存
            self._invalidate_cache(source_path, current_user)
            self._invalidate_cache(target_path, current_user)
            
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
    
    def copy_file(self, source_path: str, target_path: str, user_ip: str = None, user_agent: str = None, current_user: Dict[str, Any] = None) -> Dict[str, Any]:
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
            
            # 清理目标目录缓存
            self._invalidate_cache(target_path, current_user)
            
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
    
    def _invalidate_cache(self, file_path: str, current_user: Dict[str, Any] = None) -> None:
        """
        使相关缓存失效
        :param file_path: 文件路径
        :param current_user: 当前用户信息
        """
        try:
            # 获取用户ID
            user_id = current_user['user_id'] if current_user else 'anonymous'
            logger.info(f"开始清理缓存，文件路径: {file_path}, 用户ID: {user_id}")
            
            # 清理文件信息缓存
            file_cache_key = f"file_info:{user_id}:{hashlib.md5(file_path.encode()).hexdigest()[:16]}"
            self.cache_service.delete(file_cache_key)
            logger.info(f"清理文件信息缓存: {file_path} -> {file_cache_key}")
            
            # 清理父目录的目录列表缓存
            parent_dir = os.path.dirname(file_path) if file_path != '.' else '.'
            # 确保父目录路径格式与list_directory中的处理一致
            if parent_dir == "" or parent_dir == ".":
                parent_dir = "."
            
            dir_cache_key = f"dir_listing:{user_id}:{hashlib.md5(parent_dir.encode()).hexdigest()[:16]}"
            self.cache_service.delete(dir_cache_key)
            logger.info(f"清理父目录缓存: {parent_dir} -> {dir_cache_key}")
            
            # 清理所有相关的目录列表缓存（使用模式匹配）
            # 这确保清理所有可能的缓存变体
            pattern = "dir_listing:*"
            cleared_count = self.cache_service.clear_pattern(pattern)
            logger.info(f"清理目录列表缓存模式: {pattern}, 清理了 {cleared_count} 个键")
            
            # 清理所有文件信息缓存
            file_pattern = "file_info:*"
            cleared_file_count = self.cache_service.clear_pattern(file_pattern)
            logger.info(f"清理文件信息缓存模式: {file_pattern}, 清理了 {cleared_file_count} 个键")
            
            logger.info(f"缓存清理完成，文件路径: {file_path}")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {file_path}, 错误: {e}")
    
    def _cleanup_related_shares(self, file_path: str) -> None:
        """
        清理与源文件相关的共享文件
        :param file_path: 源文件路径
        """
        try:
            # 获取文件的绝对路径
            abs_file_path = os.path.abspath(file_path)
            
            # 查询数据库，找到所有指向该文件的共享记录
            if self.mysql_service and self.mysql_service.is_connected():
                sql = """
                SELECT shared_file_path, owner_username 
                FROM shared_files 
                WHERE original_file_path = %s AND is_active = TRUE
                """
                shared_records = self.mysql_service.execute_query(sql, (abs_file_path,))
                
                # 清理每个共享文件
                for record in shared_records:
                    shared_path = record['shared_file_path']
                    owner = record['owner_username']
                    
                    try:
                        # 如果共享文件仍然存在，删除它
                        if os.path.exists(shared_path):
                            os.remove(shared_path)
                            logger.info(f"删除共享文件: {shared_path}")
                        
                        # 更新数据库记录为非活跃状态
                        update_sql = "UPDATE shared_files SET is_active = FALSE WHERE shared_file_path = %s"
                        self.mysql_service.execute_update(update_sql, (shared_path,))
                        logger.info(f"更新共享文件记录为非活跃状态: {shared_path}")
                        
                    except Exception as e:
                        logger.error(f"清理共享文件失败: {shared_path}, 错误: {e}")
                        
        except Exception as e:
            logger.error(f"清理相关共享文件失败: {e}")
