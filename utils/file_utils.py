"""
文件工具类
提供文件操作相关的工具函数
"""

import os
import hashlib
import mimetypes
import zipfile
import tarfile
from datetime import datetime

class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def get_file_size_display(size_bytes):
        """将字节数转换为人类可读的格式"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def get_file_icon(filename):
        """根据文件扩展名返回对应的图标类名"""
        if not filename:
            return "fa-file"
        
        ext = os.path.splitext(filename)[1].lower()
        
        # 图片文件
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return "fa-image"
        
        # 文档文件
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
            return "fa-file-text"
        
        # 表格文件
        elif ext in ['.xls', '.xlsx', '.csv']:
            return "fa-table"
        
        # 演示文件
        elif ext in ['.ppt', '.pptx']:
            return "fa-presentation"
        
        # 压缩文件
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return "fa-archive"
        
        # 视频文件
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
            return "fa-video"
        
        # 音频文件
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg']:
            return "fa-music"
        
        # 代码文件
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c']:
            return "fa-code"
        
        # 可执行文件
        elif ext in ['.exe', '.msi', '.app']:
            return "fa-cog"
        
        else:
            return "fa-file"
    
    @staticmethod
    def is_image_file(filename):
        """判断是否为图片文件"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff', '.ico'}
        return os.path.splitext(filename)[1].lower() in image_extensions
    
    @staticmethod
    def is_text_file(filename):
        """判断是否为文本文件"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.log'}
        return os.path.splitext(filename)[1].lower() in text_extensions
    
    @staticmethod
    def get_mime_type(filename):
        """获取文件的MIME类型"""
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    
    @staticmethod
    def calculate_file_hash(file_path, algorithm='md5'):
        """计算文件哈希值"""
        try:
            if algorithm == 'md5':
                hash_func = hashlib.md5()
            elif algorithm == 'sha1':
                hash_func = hashlib.sha1()
            elif algorithm == 'sha256':
                hash_func = hashlib.sha256()
            else:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
        except Exception as e:
            print(f"计算文件哈希失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def create_archive(source_path, archive_path, archive_type='zip'):
        """创建压缩文件"""
        try:
            if archive_type == 'zip':
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    if os.path.isfile(source_path):
                        zipf.write(source_path, os.path.basename(source_path))
                    else:
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, source_path)
                                zipf.write(file_path, arcname)
            
            elif archive_type == 'tar':
                with tarfile.open(archive_path, 'w:gz') as tar:
                    tar.add(source_path, arcname=os.path.basename(source_path))
            
            else:
                raise ValueError(f"不支持的压缩类型: {archive_type}")
            
            print(f"压缩文件创建成功: {archive_path}")
            return True
            
        except Exception as e:
            print(f"创建压缩文件失败: {str(e)}")
            return False
    
    @staticmethod
    def extract_archive(archive_path, extract_path):
        """解压文件"""
        try:
            if archive_path.endswith('.zip'):
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(extract_path)
            
            elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(extract_path)
            
            elif archive_path.endswith('.tar'):
                with tarfile.open(archive_path, 'r') as tar:
                    tar.extractall(extract_path)
            
            else:
                raise ValueError(f"不支持的压缩文件类型: {archive_path}")
            
            print(f"文件解压成功: {extract_path}")
            return True
            
        except Exception as e:
            print(f"解压文件失败: {str(e)}")
            return False
    
    @staticmethod
    def is_safe_path(path):
        """检查路径是否安全"""
        # 允许空字符串或"."表示根目录
        if path is None:
            return False
        if path == "" or path == ".":
            return True
        
        # 检查是否包含危险字符
        dangerous_chars = ['..', '\\\\', '//', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            if char in path:
                return False
        
        # 检查是否为绝对路径，但允许项目内部的绝对路径
        if os.path.isabs(path):
            # 获取系统配置的根目录
            try:
                from core.config import config
                system_root = config.FILESYSTEM_ROOT
                # 检查路径是否在系统根目录内
                abs_path = os.path.abspath(path)
                if not abs_path.startswith(system_root):
                    return False
            except:
                # 如果无法获取配置，使用当前工作目录作为备选
                current_dir = os.getcwd()
                try:
                    abs_path = os.path.abspath(path)
                    if not abs_path.startswith(current_dir):
                        return False
                except:
                    return False
        
        # 暂时禁用系统目录检查
        # TODO: 后续需要重新启用并优化检查逻辑
        pass
        
        # 检查路径是否试图跳出当前目录
        normalized_path = os.path.normpath(path)
        if normalized_path.startswith('..') or '/..' in normalized_path or '\\..' in normalized_path:
            return False
        
        # 暂时禁用扩展名检查，允许所有文件操作
        # TODO: 后续需要重新启用并修复配置加载问题
        pass
        
        return True
    
    @staticmethod
    def get_file_info(file_path):
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            is_directory = os.path.isdir(file_path)
            
            file_info = {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size if not is_directory else 0,
                'is_directory': is_directory,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime),
                'permissions': oct(stat.st_mode)[-3:],
                'mime_type': FileUtils.get_mime_type(file_path) if not is_directory else None,
                'file_type': os.path.splitext(file_path)[1] if not is_directory else None
            }
            
            # 计算文件哈希（仅对小于10MB的文件）
            if not is_directory and stat.st_size < 10 * 1024 * 1024:
                try:
                    file_info['hash_value'] = FileUtils.calculate_file_hash(file_path)
                except:
                    file_info['hash_value'] = None
            
            return file_info
            
        except Exception as e:
            return None
    
    @staticmethod
    def format_file_size(size_bytes):
        """格式化文件大小显示"""
        return FileUtils.get_file_size_display(size_bytes)