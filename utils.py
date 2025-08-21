"""
文件管理系统工具函数
提供文件操作、安全验证、格式转换等辅助功能
"""

import os
import hashlib
import mimetypes
import shutil
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

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
            logger.error(f"计算文件哈希失败: {file_path}, 错误: {str(e)}")
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
            
            logger.info(f"压缩文件创建成功: {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"创建压缩文件失败: {str(e)}")
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
            
            logger.info(f"文件解压成功: {extract_path}")
            return True
            
        except Exception as e:
            logger.error(f"解压文件失败: {str(e)}")
            return False

class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def sanitize_filename(filename):
        """清理文件名，移除危险字符"""
        if not filename:
            return ""
        
        # 移除或替换危险字符
        dangerous_chars = {
            '<': '＜',
            '>': '＞',
            ':': '：',
            '"': '"',
            '|': '｜',
            '?': '？',
            '*': '＊',
            '\\': '＼',
            '/': '／'
        }
        
        for char, replacement in dangerous_chars.items():
            filename = filename.replace(char, replacement)
        
        # 移除控制字符
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        return filename.strip()
    
    @staticmethod
    def is_safe_file_type(filename, allowed_extensions=None, forbidden_extensions=None):
        """检查文件类型是否安全"""
        if not filename:
            return False, "文件名不能为空"
        
        ext = os.path.splitext(filename)[1].lower()
        
        # 检查禁止的文件类型
        if forbidden_extensions and ext in forbidden_extensions:
            return False, f"不允许上传 {ext} 类型的文件"
        
        # 检查允许的文件类型
        if allowed_extensions and ext not in allowed_extensions:
            return False, f"只允许上传 {', '.join(allowed_extensions)} 类型的文件"
        
        return True, "文件类型验证通过"
    
    @staticmethod
    def validate_file_size(file_size, max_size):
        """验证文件大小"""
        if file_size > max_size:
            return False, f"文件大小超过限制 ({FileUtils.get_file_size_display(max_size)})"
        return True, "文件大小验证通过"

class PathUtils:
    """路径工具类"""
    
    @staticmethod
    def normalize_path(path):
        """标准化路径"""
        if not path:
            return ""
        
        # 统一使用正斜杠
        normalized = path.replace('\\', '/')
        
        # 移除多余的斜杠
        while '//' in normalized:
            normalized = normalized.replace('//', '/')
        
        # 移除末尾斜杠（除非是根目录）
        if normalized != '/' and normalized.endswith('/'):
            normalized = normalized.rstrip('/')
        
        return normalized
    
    @staticmethod
    def get_relative_path(full_path, base_path):
        """获取相对路径"""
        try:
            return os.path.relpath(full_path, base_path).replace('\\', '/')
        except ValueError:
            return full_path
    
    @staticmethod
    def is_subpath(path, base_path):
        """检查路径是否为指定基础路径的子路径"""
        try:
            path = os.path.abspath(path)
            base_path = os.path.abspath(base_path)
            return path.startswith(base_path)
        except Exception:
            return False
    
    @staticmethod
    def get_path_depth(path):
        """获取路径深度"""
        if not path or path == '/':
            return 0
        
        normalized = PathUtils.normalize_path(path)
        return len([p for p in normalized.split('/') if p])
    
    @staticmethod
    def get_parent_path(path):
        """获取父路径"""
        if not path or path == '/':
            return ""
        
        normalized = PathUtils.normalize_path(path)
        parts = normalized.split('/')
        
        if len(parts) <= 1:
            return ""
        
        return '/'.join(parts[:-1])

class TimeUtils:
    """时间工具类"""
    
    @staticmethod
    def format_timestamp(timestamp):
        """格式化时间戳"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            
            # 如果是今天
            if dt.date() == now.date():
                return dt.strftime("今天 %H:%M")
            
            # 如果是昨天
            yesterday = now.date() - timedelta(days=1)
            if dt.date() == yesterday:
                return dt.strftime("昨天 %H:%M")
            
            # 如果是今年
            if dt.year == now.year:
                return dt.strftime("%m月%d日 %H:%M")
            
            # 其他情况
            return dt.strftime("%Y年%m月%d日 %H:%M")
            
        except Exception:
            return "未知时间"
    
    @staticmethod
    def get_file_age_display(timestamp):
        """获取文件年龄的显示文本"""
        try:
            dt = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            diff = now - dt
            
            if diff.days > 365:
                years = diff.days // 365
                return f"{years}年前"
            elif diff.days > 30:
                months = diff.days // 30
                return f"{months}个月前"
            elif diff.days > 0:
                return f"{diff.days}天前"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}小时前"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}分钟前"
            else:
                return "刚刚"
                
        except Exception:
            return "未知时间"

# 导入timedelta
from datetime import timedelta
