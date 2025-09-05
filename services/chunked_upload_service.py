"""
分块上传服务
实现大文件的分块上传、断点续传和异步处理功能
"""

import os
import hashlib
import time
import json
import shutil
import mmap
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.config import Config
from services.mysql_service import get_mysql_service
from services.cache_service import get_cache_service
from utils.logger import get_logger
from utils.file_utils import FileUtils

logger = get_logger(__name__)

class ChunkedUploadService:
    """分块上传服务类"""
    
    def __init__(self):
        self.config = Config()
        self.mysql_service = None
        self.cache_service = get_cache_service()
        
        # 分块上传配置
        self.chunk_size = 5 * 1024 * 1024  # 5MB 默认块大小，与客户端保持一致
        self.max_concurrent_chunks = 3  # 最大并发块数
        self.temp_dir = os.path.join(self.config.config_manager.get('filesystem.temp_dir', 'temp'), 'chunks')
        self.upload_timeout = 24 * 60 * 60  # 24小时上传超时
        
        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 尝试初始化MySQL服务
        try:
            self.mysql_service = get_mysql_service()
            if self.mysql_service and self.mysql_service.is_connected():
                logger.info("MySQL服务集成成功")
            else:
                logger.warning("MySQL服务不可用，将跳过数据库日志记录")
        except Exception as e:
            logger.warning(f"MySQL服务初始化失败: {e}")
    
    def _invalidate_cache(self, file_path: str, current_user: Dict[str, Any] = None) -> None:
        """清理相关缓存"""
        try:
            import hashlib
            
            # 获取用户ID
            user_id = current_user['user_id'] if current_user else 'anonymous'
            
            # 清理文件信息缓存
            file_cache_key = f"file_info:{user_id}:{hashlib.md5(file_path.encode()).hexdigest()[:16]}"
            self.cache_service.delete(file_cache_key)
            logger.debug(f"清理文件信息缓存: {file_path} -> {file_cache_key}")
            
            # 清理父目录的目录列表缓存
            parent_dir = os.path.dirname(file_path) if file_path != '.' else '.'
            dir_cache_key = f"dir_listing:{user_id}:{hashlib.md5(parent_dir.encode()).hexdigest()[:16]}"
            self.cache_service.delete(dir_cache_key)
            logger.debug(f"清理父目录缓存: {parent_dir} -> {dir_cache_key}")
            
            # 清理所有相关的目录列表缓存（使用模式匹配）
            pattern = "dir_listing:*"
            cleared_count = self.cache_service.clear_pattern(pattern)
            logger.info(f"清理目录列表缓存模式: {pattern}, 清理了 {cleared_count} 个键")
            
        except Exception as e:
            logger.error(f"清理缓存失败: {file_path}, 错误: {e}")
    
    def _generate_upload_id(self, filename: str, file_size: int, user_id: str) -> str:
        """生成唯一的上传ID"""
        timestamp = str(int(time.time()))
        content = f"{filename}_{file_size}_{user_id}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_chunk_path(self, upload_id: str, chunk_index: int) -> str:
        """获取块文件路径"""
        return os.path.join(self.temp_dir, f"{upload_id}_chunk_{chunk_index}")
    
    def _get_upload_info_path(self, upload_id: str) -> str:
        """获取上传信息文件路径"""
        return os.path.join(self.temp_dir, f"{upload_id}_info.json")
    
    def _save_upload_info(self, upload_id: str, upload_info: Dict[str, Any]):
        """保存上传信息"""
        info_path = self._get_upload_info_path(upload_id)
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(upload_info, f, ensure_ascii=False, indent=2)
    
    def _load_upload_info(self, upload_id: str) -> Optional[Dict[str, Any]]:
        """加载上传信息"""
        info_path = self._get_upload_info_path(upload_id)
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载上传信息失败: {e}")
        return None
    
    def _cleanup_upload(self, upload_id: str):
        """清理上传相关的临时文件"""
        try:
            # 删除所有块文件
            for i in range(1000):  # 假设最多1000个块
                chunk_path = self._get_chunk_path(upload_id, i)
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
                else:
                    break
            
            # 删除信息文件
            info_path = self._get_upload_info_path(upload_id)
            if os.path.exists(info_path):
                os.remove(info_path)
                
            logger.info(f"清理上传 {upload_id} 的临时文件完成")
        except Exception as e:
            logger.error(f"清理上传 {upload_id} 临时文件失败: {e}")
    
    def _cleanup_expired_uploads(self):
        """清理过期的上传"""
        try:
            current_time = time.time()
            for filename in os.listdir(self.temp_dir):
                if filename.endswith('_info.json'):
                    upload_id = filename.replace('_info.json', '')
                    info_path = os.path.join(self.temp_dir, filename)
                    
                    try:
                        with open(info_path, 'r', encoding='utf-8') as f:
                            upload_info = json.load(f)
                        
                        # 检查是否过期
                        if current_time - upload_info.get('created_at', 0) > self.upload_timeout:
                            self._cleanup_upload(upload_id)
                            logger.info(f"清理过期上传: {upload_id}")
                    except Exception as e:
                        logger.error(f"处理过期上传 {upload_id} 失败: {e}")
        except Exception as e:
            logger.error(f"清理过期上传失败: {e}")
    
    def _merge_chunks_optimized(self, upload_info: Dict[str, Any], target_path: str):
        """优化的文件块合并方法"""
        try:
            total_chunks = upload_info['total_chunks']
            chunk_size = upload_info['chunk_size']
            
            # 对于大文件，使用内存映射优化
            if upload_info['file_size'] > 100 * 1024 * 1024:  # 大于100MB
                self._merge_chunks_with_mmap(upload_info, target_path)
            else:
                # 对于小文件，使用标准方法但优化缓冲区
                self._merge_chunks_standard(upload_info, target_path)
                
        except Exception as e:
            logger.error(f"优化合并失败，回退到标准方法: {e}")
            self._merge_chunks_standard(upload_info, target_path)
    
    def _merge_chunks_with_mmap(self, upload_info: Dict[str, Any], target_path: str):
        """使用内存映射合并大文件"""
        total_chunks = upload_info['total_chunks']
        
        with open(target_path, 'wb') as output_file:
            # 预分配文件大小
            output_file.truncate(upload_info['file_size'])
            
        # 使用内存映射写入
        with open(target_path, 'r+b') as output_file:
            with mmap.mmap(output_file.fileno(), upload_info['file_size']) as mmapped_file:
                offset = 0
                
                for i in range(total_chunks):
                    chunk_path = self._get_chunk_path(upload_info['upload_id'], i)
                    
                    with open(chunk_path, 'rb') as chunk_file:
                        chunk_data = chunk_file.read()
                        mmapped_file[offset:offset + len(chunk_data)] = chunk_data
                        offset += len(chunk_data)
                    
                    # 每合并5个块输出一次进度
                    if (i + 1) % 5 == 0 or i == total_chunks - 1:
                        progress = (i + 1) / total_chunks * 100
                        logger.info(f"合并进度: {progress:.1f}% ({i+1}/{total_chunks} 块)")
    
    def _merge_chunks_standard(self, upload_info: Dict[str, Any], target_path: str):
        """标准文件块合并方法（优化版）"""
        total_chunks = upload_info['total_chunks']
        
        with open(target_path, 'wb', buffering=2*1024*1024) as output_file:  # 2MB缓冲区
            for i in range(total_chunks):
                chunk_path = self._get_chunk_path(upload_info['upload_id'], i)
                
                with open(chunk_path, 'rb', buffering=2*1024*1024) as chunk_file:  # 2MB缓冲区
                    shutil.copyfileobj(chunk_file, output_file, length=2*1024*1024)  # 2MB块大小
                
                # 每合并5个块输出一次进度
                if (i + 1) % 5 == 0 or i == total_chunks - 1:
                    progress = (i + 1) / total_chunks * 100
                    logger.info(f"合并进度: {progress:.1f}% ({i+1}/{total_chunks} 块)")
    
    def initialize_upload(self, filename: str, file_size: int, user_id: str, 
                         target_directory: str = '.', chunk_size: int = None) -> Dict[str, Any]:
        """初始化分块上传"""
        try:
            # 清理过期上传
            self._cleanup_expired_uploads()
            
            # 生成上传ID
            upload_id = self._generate_upload_id(filename, file_size, user_id)
            
            # 使用客户端发送的块大小，如果没有则使用默认值
            actual_chunk_size = chunk_size if chunk_size and chunk_size > 0 else self.chunk_size
            
            # 计算块信息
            total_chunks = (file_size + actual_chunk_size - 1) // actual_chunk_size
            
            # 创建上传信息
            upload_info = {
                'upload_id': upload_id,
                'filename': filename,
                'file_size': file_size,
                'user_id': user_id,
                'target_directory': target_directory,
                'total_chunks': total_chunks,
                'chunk_size': actual_chunk_size,  # 使用实际的块大小
                'uploaded_chunks': [],
                'created_at': time.time(),
                'updated_at': time.time(),
                'status': 'initialized'
            }
            
            # 保存上传信息
            self._save_upload_info(upload_id, upload_info)
            
            logger.info(f"初始化分块上传: {filename} ({file_size} bytes, {total_chunks} 块)")
            
            return {
                'success': True,
                'upload_id': upload_id,
                'total_chunks': total_chunks,
                'chunk_size': actual_chunk_size,  # 返回实际的块大小
                'message': '分块上传初始化成功'
            }
            
        except Exception as e:
            logger.error(f"初始化分块上传失败: {e}")
            return {
                'success': False,
                'message': f'初始化分块上传失败: {str(e)}'
            }
    
    def upload_chunk(self, upload_id: str, chunk_index: int, chunk_data: bytes, 
                    chunk_hash: str = None) -> Dict[str, Any]:
        """上传单个块"""
        try:
            # 加载上传信息
            upload_info = self._load_upload_info(upload_id)
            if not upload_info:
                return {
                    'success': False,
                    'message': '上传信息不存在或已过期'
                }
            
            # 验证块索引
            if chunk_index >= upload_info['total_chunks']:
                return {
                    'success': False,
                    'message': '块索引超出范围'
                }
            
            # 验证块大小（最后一个块可能小于chunk_size）
            chunk_size = upload_info['chunk_size']  # 使用上传信息中存储的块大小
            expected_size = chunk_size
            if chunk_index == upload_info['total_chunks'] - 1:
                expected_size = upload_info['file_size'] - chunk_index * chunk_size
            
            if len(chunk_data) != expected_size:
                return {
                    'success': False,
                    'message': f'块大小不匹配: 期望 {expected_size}, 实际 {len(chunk_data)}'
                }
            
            # 验证块哈希（如果提供）
            if chunk_hash:
                actual_hash = hashlib.md5(chunk_data).hexdigest()
                if actual_hash != chunk_hash:
                    return {
                        'success': False,
                        'message': '块哈希验证失败'
                    }
            
            # 保存块文件
            chunk_path = self._get_chunk_path(upload_id, chunk_index)
            logger.info(f"保存块文件: {chunk_path}, 大小: {len(chunk_data)} 字节")
            with open(chunk_path, 'wb') as f:
                f.write(chunk_data)
            logger.info(f"块文件保存成功: {chunk_path}")
            
            # 更新上传信息
            if chunk_index not in upload_info['uploaded_chunks']:
                upload_info['uploaded_chunks'].append(chunk_index)
                upload_info['uploaded_chunks'].sort()
                logger.info(f"块 {chunk_index} 已添加到已上传列表: {upload_info['uploaded_chunks']}")
            
            upload_info['updated_at'] = time.time()
            self._save_upload_info(upload_id, upload_info)
            
            # 检查是否所有块都已上传
            if len(upload_info['uploaded_chunks']) == upload_info['total_chunks']:
                # 检查是否已经在合并中或已合并
                if upload_info.get('status') not in ['merging', 'merged']:
                    upload_info['status'] = 'completed'
                    self._save_upload_info(upload_id, upload_info)
                    
                    # 异步合并文件
                    self._merge_file_async(upload_id)
            
            return {
                'success': True,
                'message': '块上传成功',
                'uploaded_chunks': len(upload_info['uploaded_chunks']),
                'total_chunks': upload_info['total_chunks'],
                'is_complete': len(upload_info['uploaded_chunks']) == upload_info['total_chunks']
            }
            
        except Exception as e:
            logger.error(f"上传块失败: {e}")
            return {
                'success': False,
                'message': f'上传块失败: {str(e)}'
            }
    
    def get_upload_status(self, upload_id: str) -> Dict[str, Any]:
        """获取上传状态"""
        try:
            upload_info = self._load_upload_info(upload_id)
            if not upload_info:
                return {
                    'success': False,
                    'message': '上传信息不存在或已过期'
                }
            
            return {
                'success': True,
                'upload_id': upload_id,
                'filename': upload_info['filename'],
                'file_size': upload_info['file_size'],
                'total_chunks': upload_info['total_chunks'],
                'uploaded_chunks': len(upload_info['uploaded_chunks']),
                'missing_chunks': list(set(range(upload_info['total_chunks'])) - set(upload_info['uploaded_chunks'])),
                'status': upload_info['status'],
                'progress': len(upload_info['uploaded_chunks']) / upload_info['total_chunks'] * 100,
                'created_at': upload_info['created_at'],
                'updated_at': upload_info['updated_at']
            }
            
        except Exception as e:
            logger.error(f"获取上传状态失败: {e}")
            return {
                'success': False,
                'message': f'获取上传状态失败: {str(e)}'
            }
    
    def _merge_file_async(self, upload_id: str):
        """异步合并文件"""
        def merge_task():
            try:
                # 检查是否已经在合并中
                upload_info = self._load_upload_info(upload_id)
                if upload_info and upload_info.get('status') == 'merging':
                    logger.info(f"上传 {upload_id} 已在合并中，跳过异步合并")
                    return
                
                # 设置合并状态
                if upload_info:
                    upload_info['status'] = 'merging'
                    self._save_upload_info(upload_id, upload_info)
                
                result = self._merge_file(upload_id)
                if not result.get('success'):
                    # 如果合并失败，重置状态为completed，让手动合并重试
                    upload_info = self._load_upload_info(upload_id)
                    if upload_info:
                        upload_info['status'] = 'completed'
                        self._save_upload_info(upload_id, upload_info)
                        logger.error(f"异步合并失败，重置状态为completed: {upload_id}")
            except Exception as e:
                logger.error(f"异步合并文件失败: {e}")
                # 如果异步合并失败，重置状态为completed
                try:
                    upload_info = self._load_upload_info(upload_id)
                    if upload_info:
                        upload_info['status'] = 'completed'
                        self._save_upload_info(upload_id, upload_info)
                except:
                    pass
        
        # 使用线程池执行合并任务
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(merge_task)
    
    def _merge_file(self, upload_id: str) -> Dict[str, Any]:
        """合并文件块"""
        try:
            upload_info = self._load_upload_info(upload_id)
            if not upload_info:
                return {
                    'success': False,
                    'message': '上传信息不存在'
                }
            
            # 检查是否已经合并完成
            if upload_info.get('status') == 'merged':
                return {
                    'success': True,
                    'message': '文件已合并完成',
                    'file_path': upload_info.get('target_path')
                }
            
            # 检查是否已经在合并中
            if upload_info.get('status') == 'merging':
                logger.info(f"上传 {upload_id} 已在合并中，等待完成...")
                # 等待异步合并完成，最多等待10秒
                max_wait_time = 10
                wait_interval = 0.5
                waited_time = 0
                
                while waited_time < max_wait_time:
                    time.sleep(wait_interval)
                    waited_time += wait_interval
                    upload_info = self._load_upload_info(upload_id)
                    
                    if upload_info.get('status') == 'merged':
                        return {
                            'success': True,
                            'message': '文件已合并完成',
                            'file_path': upload_info.get('target_path')
                        }
                    elif upload_info.get('status') == 'completed':
                        # 如果状态回到completed，说明异步合并失败了，我们手动合并
                        logger.info(f"异步合并失败，开始手动合并: {upload_id}")
                        break
                
                if waited_time >= max_wait_time:
                    return {
                        'success': False,
                        'message': '文件合并超时'
                    }
            
            # 设置合并状态
            upload_info['status'] = 'merging'
            self._save_upload_info(upload_id, upload_info)
            
            # 检查所有块是否都存在
            missing_chunks = []
            logger.info(f"开始检查块文件，上传ID: {upload_id}, 总块数: {upload_info['total_chunks']}")
            logger.info(f"已上传块列表: {upload_info['uploaded_chunks']}")
            
            # 如果已上传块列表为空，重新扫描块文件
            if not upload_info['uploaded_chunks']:
                logger.info("已上传块列表为空，重新扫描块文件...")
                actual_uploaded = []
                for i in range(upload_info['total_chunks']):
                    chunk_path = self._get_chunk_path(upload_id, i)
                    if os.path.exists(chunk_path):
                        actual_uploaded.append(i)
                
                logger.info(f"重新扫描到的块: {actual_uploaded}")
                upload_info['uploaded_chunks'] = actual_uploaded
                self._save_upload_info(upload_id, upload_info)
            
            for i in range(upload_info['total_chunks']):
                chunk_path = self._get_chunk_path(upload_id, i)
                exists = os.path.exists(chunk_path)
                logger.info(f"检查块 {i}: {chunk_path}, 存在: {exists}")
                if not exists:
                    missing_chunks.append(i)
            
            if missing_chunks:
                logger.error(f"缺少块文件: {missing_chunks}")
                return {
                    'success': False,
                    'message': f'缺少块: {missing_chunks}'
                }
            
            # 构建目标文件路径
            target_directory = upload_info['target_directory']
            if not os.path.exists(target_directory):
                os.makedirs(target_directory, exist_ok=True)
            
            target_path = os.path.join(target_directory, upload_info['filename'])
            
            # 检查目标文件是否已存在
            if os.path.exists(target_path):
                # 生成唯一文件名
                base_name, ext = os.path.splitext(upload_info['filename'])
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(target_directory, new_filename)
                    counter += 1
            
            # 合并文件块
            start_time = time.time()
            logger.info(f"开始合并文件块: {upload_info['total_chunks']} 个块")
            
            # 使用优化的合并方法
            self._merge_chunks_optimized(upload_info, target_path)
            
            # 验证文件大小（快速验证）
            actual_size = os.path.getsize(target_path)
            expected_size = upload_info['file_size']
            if actual_size != expected_size:
                logger.error(f"文件大小不匹配: 期望 {expected_size}, 实际 {actual_size}")
                os.remove(target_path)
                return {
                    'success': False,
                    'message': f'文件大小不匹配: 期望 {expected_size}, 实际 {actual_size}'
                }
            
            logger.info(f"文件大小验证通过: {actual_size} 字节")
            
            # 获取文件信息
            file_info = FileUtils.get_file_info(target_path)
            
            # 异步保存文件信息和记录日志，不阻塞合并完成
            def save_to_database():
                try:
                    if self.mysql_service and self.mysql_service.is_connected():
                        self.mysql_service.save_file_info(file_info)
                        logger.info("文件信息已保存到数据库")
                except Exception as e:
                    logger.error(f"保存文件信息到数据库失败: {e}")
            
            def log_operation():
                try:
                    duration_ms = int((time.time() - start_time) * 1000)
                    if self.mysql_service and self.mysql_service.is_connected():
                        self.mysql_service.log_file_operation(
                            operation_type='upload',
                            file_path=target_path,
                            file_name=file_info['name'],
                            file_size=file_info['size'],
                            user_ip='127.0.0.1',  # 分块上传时IP可能不准确
                            user_agent='ChunkedUpload',
                            status='success',
                            duration_ms=duration_ms
                        )
                        logger.info(f"操作日志已记录，耗时: {duration_ms}ms")
                except Exception as e:
                    logger.error(f"记录操作日志失败: {e}")
            
            # 异步执行数据库操作
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.submit(save_to_database)
                executor.submit(log_operation)
            
            # 清理临时文件
            self._cleanup_upload(upload_id)
            
            # 清理相关缓存
            # 从上传信息中获取用户ID，构建用户信息
            current_user = {'user_id': upload_info.get('user_id', 'anonymous')}
            self._invalidate_cache(target_path, current_user)
            
            # 更新上传状态
            upload_info['status'] = 'merged'
            upload_info['target_path'] = target_path
            upload_info['merged_at'] = time.time()
            self._save_upload_info(upload_id, upload_info)
            
            logger.info(f"文件合并成功: {target_path} ({file_info['size']} bytes)")
            
            return {
                'success': True,
                'message': '文件合并成功',
                'file_info': file_info,
                'target_path': target_path
            }
            
        except Exception as e:
            logger.error(f"合并文件失败: {e}")
            return {
                'success': False,
                'message': f'合并文件失败: {str(e)}'
            }
    
    def cancel_upload(self, upload_id: str) -> Dict[str, Any]:
        """取消上传"""
        try:
            upload_info = self._load_upload_info(upload_id)
            if not upload_info:
                return {
                    'success': False,
                    'message': '上传信息不存在'
                }
            
            # 清理临时文件
            self._cleanup_upload(upload_id)
            
            logger.info(f"取消上传: {upload_id}")
            
            return {
                'success': True,
                'message': '上传已取消'
            }
            
        except Exception as e:
            logger.error(f"取消上传失败: {e}")
            return {
                'success': False,
                'message': f'取消上传失败: {str(e)}'
            }
    
    def get_upload_list(self, user_id: str = None) -> Dict[str, Any]:
        """获取上传列表"""
        try:
            uploads = []
            
            for filename in os.listdir(self.temp_dir):
                if filename.endswith('_info.json'):
                    upload_id = filename.replace('_info.json', '')
                    info_path = os.path.join(self.temp_dir, filename)
                    
                    try:
                        with open(info_path, 'r', encoding='utf-8') as f:
                            upload_info = json.load(f)
                        
                        # 如果指定了用户ID，只返回该用户的上传
                        if user_id and upload_info.get('user_id') != user_id:
                            continue
                        
                        uploads.append({
                            'upload_id': upload_id,
                            'filename': upload_info['filename'],
                            'file_size': upload_info['file_size'],
                            'total_chunks': upload_info['total_chunks'],
                            'uploaded_chunks': len(upload_info['uploaded_chunks']),
                            'status': upload_info['status'],
                            'progress': len(upload_info['uploaded_chunks']) / upload_info['total_chunks'] * 100,
                            'created_at': upload_info['created_at'],
                            'updated_at': upload_info['updated_at']
                        })
                    except Exception as e:
                        logger.error(f"处理上传信息 {upload_id} 失败: {e}")
            
            return {
                'success': True,
                'uploads': uploads,
                'total': len(uploads)
            }
            
        except Exception as e:
            logger.error(f"获取上传列表失败: {e}")
            return {
                'success': False,
                'message': f'获取上传列表失败: {str(e)}'
            }
