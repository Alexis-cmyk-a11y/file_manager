"""
安全服务
提供文件系统安全检查和权限控制
"""

import os
import re
import mimetypes
import hashlib
from pathlib import Path, PurePath
from typing import Tuple, List, Dict, Any, Optional
from core.config import Config
from utils.logger import get_logger
from services.mysql_service import get_mysql_service

logger = get_logger(__name__)

class SecurityService:
    """安全服务类"""
    
    def __init__(self):
        self.config = Config()
        self.mysql_service = get_mysql_service()
        self._init_forbidden_patterns()
    
    def _init_forbidden_patterns(self):
        """初始化禁止的模式"""
        # 危险字符模式
        self.dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        
        # Windows保留名称
        self.reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        # 危险文件扩展名
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar',
            '.msi', '.msu', '.ps1', '.psm1', '.psd1', '.psc1', '.psc2'
        }
        
        # 路径遍历模式
        self.path_traversal_patterns = [
            r'\.\.',  # ..
            r'\.\./',  # ../
            r'\.\.\\',  # ..\
            r'%2e%2e',  # URL编码的..
            r'%2e%2e%2f',  # URL编码的../
            r'%2e%2e%5c',  # URL编码的..\
        ]
    
    def validate_path_safety(self, rel_path: str) -> Tuple[bool, str]:
        """验证路径安全性
        
        Args:
            rel_path: 相对路径
            
        Returns:
            Tuple[bool, str]: (是否安全, 结果信息或绝对路径)
        """
        try:
            # 1. 基本路径验证
            if not self._validate_basic_path(rel_path):
                return False, "路径格式无效"
            
            # 2. 路径遍历检查
            if self._contains_path_traversal(rel_path):
                logger.warning(f"检测到路径遍历攻击: {rel_path}")
                return False, "路径包含非法字符"
            
            # 3. 构建绝对路径
            root_dir = self.config.ROOT_DIR
            full_path = os.path.abspath(os.path.join(root_dir, rel_path))
            
            # 4. 检查是否在根目录范围内
            if not full_path.startswith(os.path.abspath(root_dir)):
                logger.warning(f"路径超出根目录范围: {rel_path} -> {full_path}")
                return False, "路径超出允许范围"
            
            # 5. 规范化路径
            normalized_path = os.path.normpath(full_path)
            
            return True, normalized_path
            
        except Exception as e:
            logger.error(f"路径安全检查失败: {rel_path}, 错误: {e}")
            return False, f"路径验证异常: {str(e)}"
    
    def _validate_basic_path(self, path: str) -> bool:
        """验证基本路径格式"""
        if not path:
            return True  # 空路径表示根目录
        
        # 检查路径长度
        if len(path) > 4096:  # 最大路径长度
            return False
        
        # 检查是否包含空字符
        if '\x00' in path:
            return False
        
        return True
    
    def _contains_path_traversal(self, path: str) -> bool:
        """检查是否包含路径遍历"""
        path_lower = path.lower()
        
        # 检查各种路径遍历模式
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path_lower):
                return True
        
        # 检查URL编码的路径遍历
        try:
            import urllib.parse
            decoded_path = urllib.parse.unquote(path)
            if '..' in decoded_path:
                return True
        except Exception:
            pass
        
        return False
    
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """验证文件名安全性
        
        Args:
            filename: 文件名
            
        Returns:
            Tuple[bool, str]: (是否安全, 错误信息或文件名)
        """
        try:
            # 1. 基本检查
            if not filename or not filename.strip():
                return False, "文件名不能为空"
            
            # 2. 长度检查
            if len(filename) > 255:
                return False, "文件名过长（最大255字符）"
            
            # 3. 危险字符检查
            for char in self.dangerous_chars:
                if char in filename:
                    return False, f"文件名包含危险字符: {char}"
            
            # 4. 保留名称检查
            name_without_ext = os.path.splitext(filename)[0].upper()
            if name_without_ext in self.reserved_names:
                return False, f"文件名是系统保留名称: {filename}"
            
            # 5. 特殊模式检查
            if self._contains_special_patterns(filename):
                return False, "文件名包含特殊模式"
            
            # 6. 扩展名检查
            if not self._validate_extension(filename):
                return False, "文件扩展名不被允许"
            
            return True, filename.strip()
            
        except Exception as e:
            logger.error(f"文件名验证失败: {filename}, 错误: {e}")
            return False, f"文件名验证异常: {str(e)}"
    
    def _contains_special_patterns(self, filename: str) -> bool:
        """检查是否包含特殊模式"""
        # 检查隐藏文件
        if filename.startswith('.'):
            return False  # 允许隐藏文件
        
        # 检查Windows隐藏文件
        if filename.startswith('~$'):
            return False  # 允许临时文件
        
        # 检查其他特殊模式
        suspicious_patterns = [
            r'^desktop\.ini$',
            r'^thumbs\.db$',
            r'^\.ds_store$',
            r'^\.gitignore$',
            r'^\.env$',
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, filename.lower()):
                return False  # 这些是正常的系统文件
        
        return False
    
    def _validate_extension(self, filename: str) -> bool:
        """验证文件扩展名"""
        if not self.config.ALLOW_EXECUTABLE_FILES:
            _, ext = os.path.splitext(filename.lower())
            if ext in self.dangerous_extensions:
                return False
        
        return True
    
    def validate_file_type(self, file_path: str, mime_type: str = None) -> Tuple[bool, str]:
        """验证文件类型安全性
        
        Args:
            file_path: 文件路径
            mime_type: MIME类型（可选）
            
        Returns:
            Tuple[bool, str]: (是否安全, 错误信息或MIME类型)
        """
        try:
            # 移除扩展名检查，允许所有文件类型
            
            # MIME类型检查（可选）
            if mime_type:
                if not self._validate_mime_type(mime_type):
                    return False, f"MIME类型 {mime_type} 不被允许"
                return True, mime_type
            
            # 基于扩展名的MIME类型推断
            inferred_mime_type = mimetypes.guess_type(file_path)[0]
            if inferred_mime_type and not self._validate_mime_type(inferred_mime_type):
                return False, f"推断的MIME类型 {inferred_mime_type} 不被允许"
            
            return True, inferred_mime_type or "application/octet-stream"
            
        except Exception as e:
            logger.error(f"文件类型验证失败: {file_path}, 错误: {e}")
            return False, f"文件类型验证异常: {str(e)}"
    
    def _validate_mime_type(self, mime_type: str) -> bool:
        """验证MIME类型"""
        # 危险MIME类型
        dangerous_mimes = {
            'application/x-executable',
            'application/x-msdownload',
            'application/x-msi',
            'application/x-ms-shortcut',
            'application/x-msdos-program',
            'application/x-msi',
            'application/x-msu',
            'application/x-powershell',
            'text/javascript',
            'application/javascript',
            'application/x-javascript',
        }
        
        if mime_type in dangerous_mimes:
            return False
        
        # 检查可执行文件
        if not self.config.ALLOW_EXECUTABLE_FILES:
            if mime_type.startswith('application/x-executable'):
                return False
        
        return True
    
    def validate_file_size(self, file_size: int) -> Tuple[bool, str]:
        """验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            
        Returns:
            Tuple[bool, str]: (是否允许, 错误信息或大小信息)
        """
        try:
            max_size = self.config.MAX_FILE_SIZE
            
            if file_size > max_size:
                size_mb = file_size / (1024 * 1024)
                max_size_mb = max_size / (1024 * 1024)
                return False, f"文件过大: {size_mb:.1f}MB，最大允许: {max_size_mb:.1f}MB"
            
            return True, f"文件大小: {file_size} 字节"
            
        except Exception as e:
            logger.error(f"文件大小验证失败: {file_size}, 错误: {e}")
            return False, f"文件大小验证异常: {str(e)}"
    
    def sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除或替换危险字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        try:
            # 替换危险字符
            sanitized = filename
            for char in self.dangerous_chars:
                sanitized = sanitized.replace(char, '_')
            
            # 移除多余的下划线
            sanitized = re.sub(r'_+', '_', sanitized)
            
            # 移除首尾的下划线和空格
            sanitized = sanitized.strip('_ ')
            
            # 如果清理后为空，使用默认名称
            if not sanitized:
                sanitized = "unnamed_file"
            
            return sanitized
            
        except Exception as e:
            logger.error(f"文件名清理失败: {filename}, 错误: {e}")
            return "unnamed_file"
    
    def get_security_report(self, file_path: str) -> Dict[str, Any]:
        """获取文件安全报告
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 安全报告
        """
        try:
            report = {
                'file_path': file_path,
                'security_checks': {},
                'overall_safe': True,
                'warnings': [],
                'errors': []
            }
            
            # 路径安全检查
            path_safe, path_result = self.validate_path_safety(file_path)
            report['security_checks']['path_safety'] = {
                'safe': path_safe,
                'result': path_result
            }
            if not path_safe:
                report['overall_safe'] = False
                report['errors'].append(f"路径不安全: {path_result}")
            
            # 文件名检查
            filename = os.path.basename(file_path)
            name_safe, name_result = self.validate_filename(filename)
            report['security_checks']['filename_safety'] = {
                'safe': name_safe,
                'result': name_result
            }
            if not name_safe:
                report['overall_safe'] = False
                report['errors'].append(f"文件名不安全: {name_result}")
            
            # 文件类型检查
            type_safe, type_result = self.validate_file_type(file_path)
            report['security_checks']['file_type'] = {
                'safe': type_safe,
                'result': type_result
            }
            if not type_safe:
                report['overall_safe'] = False
                report['errors'].append(f"文件类型不安全: {type_result}")
            
            # 文件大小检查（如果文件存在）
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                size_safe, size_result = self.validate_file_size(file_size)
                report['security_checks']['file_size'] = {
                    'safe': size_safe,
                    'result': size_result,
                    'size_bytes': file_size
                }
                if not size_safe:
                    report['overall_safe'] = False
                    report['warnings'].append(f"文件大小警告: {size_result}")
            
            return report
            
        except Exception as e:
            logger.error(f"生成安全报告失败: {file_path}, 错误: {e}")
            return {
                'file_path': file_path,
                'overall_safe': False,
                'errors': [f"安全报告生成失败: {str(e)}"]
            }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """记录安全事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
        """
        try:
            security_info = {
                'event_type': event_type,
                'timestamp': details.get('timestamp'),
                'user_ip': details.get('user_ip'),
                'user_agent': details.get('user_agent'),
                'file_path': details.get('file_path'),
                'operation': details.get('operation'),
                'risk_level': details.get('risk_level', 'medium'),
                'details': details
            }
            
            logger.warning(
                f"安全事件: {event_type}",
                security_event=True,
                **security_info
            )
            
        except Exception as e:
            logger.error(f"记录安全事件失败: {event_type}, 错误: {e}")

    def check_user_directory_access(self, user_id: int, user_email: str, directory_path: str) -> bool:
        """
        检查用户是否有权限访问指定目录
        
        Args:
            user_id: 用户ID
            user_email: 用户邮箱
            directory_path: 要访问的目录路径
            
        Returns:
            bool: 是否有权限访问
        """
        try:
            # 管理员可以访问所有目录
            if user_email == 'admin@system.local':
                return True
            
            # 获取用户信息
            user_info = self.mysql_service.get_user_by_id(user_id)
            if not user_info:
                logger.warning(f"用户不存在: {user_id}")
                return False
            
            # 检查用户角色
            if user_info.get('role') == 'admin':
                return True
            
            # 普通用户只能访问自己的目录
            username = user_email.split('@')[0]  # 从邮箱提取用户名
            user_directory = os.path.join('home', 'users', username)
            
            # 规范化路径
            normalized_directory_path = os.path.normpath(directory_path)
            normalized_user_directory = os.path.normpath(user_directory)
            
            # 检查路径是否在用户目录内
            if normalized_directory_path == '.' or normalized_directory_path == '':
                # 根目录访问，重定向到用户目录
                return True
            
            # 检查是否在用户目录内
            if normalized_directory_path.startswith(normalized_user_directory):
                return True
            
            # 检查是否在共享目录内（用户可以访问共享目录）
            shared_directory = os.path.join('home', 'shared')
            normalized_shared_directory = os.path.normpath(shared_directory)
            if normalized_directory_path.startswith(normalized_shared_directory):
                return True
            
            logger.warning(f"用户 {user_email} 尝试访问未授权目录: {directory_path}")
            return False
            
        except Exception as e:
            logger.error(f"检查用户目录权限失败: {e}")
            return False
    
    def get_user_root_directory(self, user_id: int, user_email: str) -> str:
        """
        获取用户的根目录路径
        
        Args:
            user_id: 用户ID
            user_email: 用户邮箱
            
        Returns:
            str: 用户的根目录路径
        """
        try:
            # 获取系统配置的根目录
            from core.config import config
            system_root = config.FILESYSTEM_ROOT
            
            # 管理员可以访问系统根目录
            if user_email == 'admin@system.local':
                return system_root
            
            # 获取用户信息
            user_info = self.mysql_service.get_user_by_id(user_id)
            if not user_info:
                logger.warning(f"用户不存在: {user_id}")
                return system_root
            
            # 检查用户角色
            if user_info.get('role') == 'admin':
                return system_root
            
            # 普通用户返回自己的目录
            username = user_email.split('@')[0]  # 从邮箱提取用户名
            user_directory = os.path.join(system_root, 'home', 'users', username)
            
            # 确保用户目录存在
            if not os.path.exists(user_directory):
                os.makedirs(user_directory, exist_ok=True)
                logger.info(f"创建用户目录: {user_directory}")
            
            return user_directory
            
        except Exception as e:
            logger.error(f"获取用户根目录失败: {e}")
            # 回退到配置文件中的根目录
            try:
                from core.config import config
                return config.FILESYSTEM_ROOT
            except:
                return '.'
    
    def sanitize_path_for_user(self, user_id: int, user_email: str, directory_path: str) -> str:
        """
        为用户清理和验证路径
        
        Args:
            user_id: 用户ID
            user_email: 用户邮箱
            directory_path: 原始路径
            
        Returns:
            str: 清理后的安全路径
        """
        try:
            # 获取系统配置的根目录
            from core.config import config
            system_root = config.FILESYSTEM_ROOT
            
            # 管理员可以访问所有路径
            if user_email == 'admin@system.local':
                # 如果管理员访问根目录，返回系统根目录
                if directory_path == '.' or directory_path == '':
                    return system_root
                return directory_path
            
            # 获取用户信息
            user_info = self.mysql_service.get_user_by_id(user_id)
            if not user_info:
                logger.warning(f"用户不存在: {user_id}")
                return system_root
            
            # 检查用户角色
            if user_info.get('role') == 'admin':
                # 如果管理员访问根目录，返回系统根目录
                if directory_path == '.' or directory_path == '':
                    return system_root
                return directory_path
            
            # 普通用户路径处理
            if directory_path == '.' or directory_path == '':
                # 根目录访问，重定向到用户目录
                return self.get_user_root_directory(user_id, user_email)
            
            # 规范化路径
            normalized_path = os.path.normpath(directory_path)
            
            # 检查是否在用户目录内
            username = user_email.split('@')[0]
            user_directory = os.path.join(system_root, 'home', 'users', username)
            normalized_user_directory = os.path.normpath(user_directory)
            
            if normalized_path.startswith(normalized_user_directory):
                return normalized_path
            
            # 检查是否在共享目录内
            shared_directory = os.path.join(system_root, 'home', 'shared')
            normalized_shared_directory = os.path.normpath(shared_directory)
            if normalized_path.startswith(normalized_shared_directory):
                return normalized_path
            
            # 如果路径不在允许的范围内，重定向到用户目录
            logger.warning(f"用户 {user_email} 访问未授权路径，重定向到用户目录: {directory_path}")
            return self.get_user_root_directory(user_id, user_email)
            
        except Exception as e:
            logger.error(f"清理用户路径失败: {e}")
            return self.get_user_root_directory(user_id, user_email)

# 全局安全服务实例
_security_service = None

def get_security_service() -> SecurityService:
    """获取安全服务实例"""
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service
