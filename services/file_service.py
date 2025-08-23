"""
文件操作服务
提供文件系统操作的核心业务逻辑
"""

import os
import shutil
from datetime import datetime
import hashlib
import mimetypes

from core.config import Config
from services.security_service import SecurityService
from utils.file_utils import FileUtils
from utils.logger import get_logger

logger = get_logger(__name__)

class FileService:
    """文件操作服务类"""
    
    def __init__(self):
        self.config = Config()
        self.security_service = SecurityService()
        self.file_utils = FileUtils()
    
    def list_directory(self, rel_path):
        """列出指定目录下的所有文件和子目录"""
        # 验证路径安全性
        is_safe, result = self.security_service.validate_path_safety(rel_path)
        if not is_safe:
            logger.warning(f"路径安全检查失败: {rel_path}")
            return {'success': False, 'message': result}
        
        full_path = result
        logger.info(f"列出目录内容: {full_path}")
        
        # 检查路径是否存在
        if not os.path.exists(full_path):
            logger.warning(f"请求的路径不存在: {full_path}")
            return {'success': False, 'message': '路径不存在'}
        
        if not os.path.isdir(full_path):
            logger.warning(f"请求的路径不是目录: {full_path}")
            return {'success': False, 'message': '请求的路径不是目录'}

        try:
            items = self._get_directory_items(full_path, rel_path)
            
            # 计算目录统计信息
            total_files = len([item for item in items if item['type'] == 'file'])
            total_dirs = len([item for item in items if item['type'] == 'directory'])
            total_size = sum(item['size'] for item in items if item['type'] == 'file')
            
            logger.debug(f"目录 {full_path} 中找到 {len(items)} 个项目")
            return {
                'success': True,
                'path': rel_path,
                'items': items,
                'current_dir': full_path,
                'stats': {
                    'total_items': len(items),
                    'total_files': total_files,
                    'total_directories': total_dirs,
                    'total_size': total_size
                }
            }
        except Exception as e:
            logger.error(f"列出目录内容失败: {full_path}, 错误: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def copy_item(self, source_path, target_dir):
        """复制文件或目录"""
        # 验证源路径安全性
        is_safe_source, source_result = self.security_service.validate_path_safety(source_path)
        if not is_safe_source:
            return {'success': False, 'message': source_result}
        
        # 验证目标路径安全性
        is_safe_target, target_result = self.security_service.validate_path_safety(target_dir)
        if not is_safe_target:
            return {'success': False, 'message': target_result}
        
        full_source_path = source_result
        full_target_dir = target_result
        
        logger.info(f"尝试复制: {full_source_path} 到 {full_target_dir}")
        
        # 检查源路径是否存在
        if not os.path.exists(full_source_path):
            logger.warning(f"源文件或目录不存在: {full_source_path}")
            return {'success': False, 'message': '源文件或目录不存在'}
        
        # 检查目标目录是否存在
        if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
            logger.warning(f"目标目录不存在: {full_target_dir}")
            return {'success': False, 'message': '目标目录不存在'}
        
        try:
            # 获取源文件/目录名
            source_name = os.path.basename(full_source_path)
            target_path = os.path.join(full_target_dir, source_name)
            
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                logger.warning(f"目标路径已存在同名文件或目录: {target_path}")
                return {'success': False, 'message': f'目标路径已存在同名文件或目录: {source_name}'}
            
            # 复制文件或目录
            is_file = os.path.isfile(full_source_path)
            if is_file:
                shutil.copy2(full_source_path, target_path)
                logger.info(f"文件复制成功: {full_source_path} -> {target_path}")
            else:
                shutil.copytree(full_source_path, target_path)
                logger.info(f"目录复制成功: {full_source_path} -> {target_path}")
            
            return {
                'success': True,
                'message': f'{"文件" if is_file else "目录"} {source_name} 复制成功'
            }
        except Exception as e:
            logger.error(f"复制失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def move_item(self, source_path, target_dir):
        """移动文件或目录"""
        # 验证路径安全性
        is_safe_source, source_result = self.security_service.validate_path_safety(source_path)
        if not is_safe_source:
            return {'success': False, 'message': source_result}
        
        is_safe_target, target_result = self.security_service.validate_path_safety(target_dir)
        if not is_safe_target:
            return {'success': False, 'message': target_result}
        
        full_source_path = source_result
        full_target_dir = target_result
        
        logger.info(f"尝试移动: {full_source_path} 到 {full_target_dir}")
        
        # 检查源路径和目标目录是否存在
        if not os.path.exists(full_source_path):
            logger.warning(f"源文件或目录不存在: {full_source_path}")
            return {'success': False, 'message': '源文件或目录不存在'}
        
        if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
            logger.warning(f"目标目录不存在: {full_target_dir}")
            return {'success': False, 'message': '目标目录不存在'}
        
        try:
            # 获取源文件/目录名
            source_name = os.path.basename(full_source_path)
            target_path = os.path.join(full_target_dir, source_name)
            
            # 检查目标路径是否已存在
            if os.path.exists(target_path):
                logger.warning(f"目标路径已存在同名文件或目录: {target_path}")
                return {'success': False, 'message': f'目标路径已存在同名文件或目录: {source_name}'}
            
            # 移动文件或目录
            is_file = os.path.isfile(full_source_path)
            shutil.move(full_source_path, target_path)
            logger.info(f"{'文件' if is_file else '目录'}移动成功: {full_source_path} -> {target_path}")
            
            return {
                'success': True,
                'message': f'{"文件" if is_file else "目录"} {source_name} 移动成功'
            }
        except Exception as e:
            logger.error(f"移动失败: {str(e)}")
            return {'success': False, 'message': '移动操作失败，请稍后重试'}
    
    def delete_item(self, path):
        """删除文件或目录"""
        # 验证路径安全性
        is_safe, result = self.security_service.validate_path_safety(path)
        if not is_safe:
            return {'success': False, 'message': result}
        
        full_path = result
        logger.info(f"尝试删除: {path}")
        
        # 检查路径是否存在
        if not os.path.exists(full_path):
            logger.warning(f"要删除的文件或目录不存在: {full_path}")
            return {'success': False, 'message': '文件或目录不存在'}
        
        try:
            # 删除文件或目录
            item_name = os.path.basename(full_path)
            is_file = os.path.isfile(full_path)
            if is_file:
                os.remove(full_path)
                item_type = '文件'
                logger.info(f"文件删除成功: {full_path}")
            else:
                shutil.rmtree(full_path)
                item_type = '目录'
                logger.info(f"目录删除成功: {full_path}")
            
            return {
                'success': True,
                'message': f'{item_type} {item_name} 删除成功'
            }
        except PermissionError:
            logger.error(f"没有权限删除: {full_path}")
            return {'success': False, 'message': '没有权限删除此文件或目录'}
        except Exception as e:
            logger.error(f"删除失败: {str(e)}")
            return {'success': False, 'message': '删除操作失败，请稍后重试'}
    
    def create_folder(self, parent_dir, folder_name):
        """创建新文件夹"""
        # 检查文件夹名是否有效
        if not folder_name or folder_name.strip() == '':
            return {'success': False, 'message': '文件夹名不能为空'}
        
        # 检查文件夹名是否包含非法字符
        invalid_chars = '<>:"|?*'
        if any(char in folder_name for char in invalid_chars):
            return {'success': False, 'message': f'文件夹名不能包含以下字符: {invalid_chars}'}
        
        # 验证父目录路径安全性
        is_safe, result = self.security_service.validate_path_safety(parent_dir)
        if not is_safe:
            return {'success': False, 'message': result}
        
        full_parent_dir = result
        full_path = os.path.join(full_parent_dir, folder_name)
        
        # 检查父目录是否存在
        if not os.path.exists(full_parent_dir) or not os.path.isdir(full_parent_dir):
            return {'success': False, 'message': '父目录不存在'}
        
        # 检查文件夹是否已存在
        if os.path.exists(full_path):
            return {'success': False, 'message': f'文件夹 {folder_name} 已存在'}
        
        try:
            # 创建文件夹
            os.makedirs(full_path)
            logger.info(f"文件夹创建成功: {full_path}")
            
            return {
                'success': True,
                'message': f'文件夹 {folder_name} 创建成功',
                'folder': {
                    'name': folder_name,
                    'path': os.path.join(parent_dir, folder_name).replace('\\', '/'),
                    'type': 'directory'
                }
            }
        except Exception as e:
            logger.error(f"创建文件夹失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def rename_item(self, path, new_name):
        """重命名文件或目录"""
        # 检查新名称是否有效
        if not new_name or new_name.strip() == '':
            return {'success': False, 'message': '新名称不能为空'}
        
        # 检查新名称是否包含非法字符
        invalid_chars = '<>:"|?*'
        if any(char in new_name for char in invalid_chars):
            return {'success': False, 'message': f'新名称不能包含以下字符: {invalid_chars}'}
        
        # 验证路径安全性
        is_safe, result = self.security_service.validate_path_safety(path)
        if not is_safe:
            return {'success': False, 'message': result}
        
        full_path = result
        
        # 检查路径是否存在
        if not os.path.exists(full_path):
            return {'success': False, 'message': '文件或目录不存在'}
        
        try:
            # 获取父目录和新路径
            parent_dir = os.path.dirname(full_path)
            new_path = os.path.join(parent_dir, new_name)
            
            # 检查新路径是否已存在
            if os.path.exists(new_path):
                return {'success': False, 'message': f'已存在同名文件或目录: {new_name}'}
            
            # 重命名文件或目录
            os.rename(full_path, new_path)
            logger.info(f"重命名成功: {full_path} -> {new_path}")
            
            # 计算相对路径
            rel_parent_dir = os.path.dirname(path)
            rel_new_path = os.path.join(rel_parent_dir, new_name).replace('\\', '/')
            
            return {
                'success': True,
                'message': f'{"文件" if os.path.isfile(new_path) else "目录"} 重命名成功',
                'new_path': rel_new_path,
                'new_name': new_name
            }
        except Exception as e:
            logger.error(f"重命名失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _get_directory_items(self, directory_path, relative_path):
        """获取目录内容并返回格式化列表"""
        items = []
        try:
            for item in os.listdir(directory_path):
                try:
                    item_path = os.path.join(directory_path, item)
                    file_info = self._get_file_info(item_path)
                    if file_info:
                        file_info['path'] = os.path.join(relative_path, item).replace('\\', '/')
                        items.append(file_info)
                except Exception as item_error:
                    logger.error(f"获取文件信息失败: {item}, 错误: {str(item_error)}")
            
            # 按类型和名称排序：先目录后文件，同类型按名称排序
            items.sort(key=lambda x: (0 if x['type'] == 'directory' else 1, x['name'].lower()))
            return items
        except PermissionError:
            logger.error(f"没有权限访问目录: {directory_path}")
            return []
        except Exception as e:
            logger.error(f"读取目录失败: {directory_path}, 错误: {str(e)}")
            return []
    
    def _get_file_info(self, file_path):
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            file_info = {
                'name': os.path.basename(file_path),
                'type': 'directory' if os.path.isdir(file_path) else 'file',
                'size': stat.st_size if os.path.isfile(file_path) else 0,
                'modified': int(stat.st_mtime),
                'created': int(stat.st_ctime),
                'permissions': oct(stat.st_mode)[-3:],
                'mime_type': mimetypes.guess_type(file_path)[0] if os.path.isfile(file_path) else None
            }
            
            # 计算文件哈希（仅对文件）
            if os.path.isfile(file_path) and stat.st_size < 10 * 1024 * 1024:  # 小于10MB的文件
                try:
                    with open(file_path, 'rb') as f:
                        file_info['md5'] = hashlib.md5(f.read()).hexdigest()
                except:
                    file_info['md5'] = None
            
            return file_info
        except Exception as e:
            logger.error(f"获取文件信息失败: {file_path}, 错误: {str(e)}")
            return None
