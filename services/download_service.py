"""
下载服务
处理文件下载的业务逻辑
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Tuple
from flask import send_file, Response, request
from urllib.parse import urlparse

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
        
        # 确保download目录存在
        self.download_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'download')
        os.makedirs(self.download_dir, exist_ok=True)
    
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
    
    def download_web_file(self, url: str, filename: str = None, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """从公网下载文件到服务器的download目录"""
        start_time = time.time()
        
        try:
            # 验证URL
            if not self._is_valid_url(url):
                return {
                    'success': False,
                    'message': '无效的URL格式'
                }
            
            # 如果没有指定文件名，从URL中提取
            if not filename:
                filename = self._extract_filename_from_url(url)
            
            # 确保文件名安全
            filename = self._sanitize_filename(filename)
            
            # 构建本地文件路径
            local_file_path = os.path.join(self.download_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(local_file_path):
                return {
                    'success': False,
                    'message': f'文件 {filename} 已存在，请使用不同的文件名'
                }
            
            # 下载文件
            logger.info(f"开始从 {url} 下载文件到 {local_file_path}")
            
            # 设置请求头，模拟浏览器行为
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 流式下载大文件
            with requests.get(url, headers=headers, stream=True, timeout=30) as response:
                response.raise_for_status()
                
                # 获取文件大小
                file_size = int(response.headers.get('content-length', 0))
                
                # 写入文件
                with open(local_file_path, 'wb') as f:
                    downloaded_size = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
                
                # 验证文件大小
                actual_size = os.path.getsize(local_file_path)
                if file_size > 0 and actual_size != file_size:
                    os.remove(local_file_path)
                    return {
                        'success': False,
                        'message': f'文件下载不完整，期望大小: {file_size}, 实际大小: {actual_size}'
                    }
            
            # 记录操作日志
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='web_download',
                file_path=local_file_path,
                file_name=filename,
                file_size=actual_size,
                user_ip=user_ip,
                user_agent=user_agent,
                status='success',
                duration_ms=duration_ms
            )
            
            logger.info(f"文件下载成功: {filename}, 大小: {actual_size} 字节")
            
            return {
                'success': True,
                'message': f'文件 {filename} 下载成功',
                'filename': filename,
                'local_path': local_file_path,
                'file_size': actual_size,
                'download_url': url
            }
            
        except requests.exceptions.RequestException as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='web_download',
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=f'网络请求失败: {str(e)}',
                duration_ms=duration_ms
            )
            return {
                'success': False,
                'message': f'网络请求失败: {str(e)}'
            }
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_operation(
                operation_type='web_download',
                user_ip=user_ip,
                user_agent=user_agent,
                status='failed',
                error_message=str(e),
                duration_ms=duration_ms
            )
            return {
                'success': False,
                'message': f'下载失败: {str(e)}'
            }
    
    def list_downloaded_files(self) -> Dict[str, Any]:
        """列出download目录中的所有文件"""
        try:
            if not os.path.exists(self.download_dir):
                return {
                    'success': True,
                    'files': [],
                    'message': 'download目录不存在'
                }
            
            files = []
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.isfile(file_path):
                    file_info = FileUtils.get_file_info(file_path)
                    files.append({
                        'name': filename,
                        'size': file_info['size'],
                        'modified_time': file_info['modified_time'],
                        'path': file_path
                    })
            
            # 按修改时间排序，最新的在前
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            
            return {
                'success': True,
                'files': files,
                'total_count': len(files),
                'download_dir': self.download_dir
            }
            
        except Exception as e:
            logger.error(f"获取下载文件列表失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def delete_downloaded_file(self, filename: str, user_ip: str = None, user_agent: str = None) -> Dict[str, Any]:
        """删除download目录中的文件"""
        try:
            file_path = os.path.join(self.download_dir, filename)
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'message': '文件不存在'
                }
            
            if not os.path.isfile(file_path):
                return {
                    'success': False,
                    'message': '路径不是文件'
                }
            
            # 获取文件信息用于日志记录
            file_info = FileUtils.get_file_info(file_path)
            
            # 删除文件
            os.remove(file_path)
            
            # 记录操作日志
            self._log_operation(
                operation_type='delete_downloaded_file',
                file_path=file_path,
                file_name=filename,
                file_size=file_info['size'],
                user_ip=user_ip,
                user_agent=user_agent,
                status='success'
            )
            
            return {
                'success': True,
                'message': f'文件 {filename} 删除成功'
            }
            
        except Exception as e:
            logger.error(f"删除下载文件失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _is_valid_url(self, url: str) -> bool:
        """验证URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                # 如果没有文件名或扩展名，生成一个
                import hashlib
                filename = f"downloaded_file_{hashlib.md5(url.encode()).hexdigest()[:8]}.tmp"
            return filename
        except:
            return "downloaded_file.tmp"
    
    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全字符"""
        import re
        # 移除或替换不安全的字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # 限制文件名长度
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        return filename
