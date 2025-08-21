"""
上传服务
处理文件上传的业务逻辑
"""

import os
import hashlib
import logging
from werkzeug.utils import secure_filename

from core.config import Config
from services.security_service import SecurityService

logger = logging.getLogger(__name__)

class UploadService:
    """上传服务类"""
    
    def __init__(self):
        self.config = Config()
        self.security_service = SecurityService()
    
    def upload_files(self, files, target_dir):
        """上传多个文件"""
        # 检查是否启用上传功能
        if not self.config.ENABLE_UPLOAD:
            logger.warning("尝试上传文件，但上传功能已禁用")
            return {'success': False, 'message': '上传功能已禁用'}
        
        # 验证目标目录路径安全性
        is_safe, result = self.security_service.validate_path_safety(target_dir)
        if not is_safe:
            logger.warning(f"上传目标路径安全检查失败: {target_dir}")
            return {'success': False, 'message': result}
        
        full_target_dir = result
        logger.info(f"尝试上传文件到目录: {full_target_dir}")
        
        # 检查目标目录是否存在
        if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
            logger.warning(f"上传目标目录不存在: {full_target_dir}")
            return {'success': False, 'message': '目标目录不存在'}
        
        try:
            uploaded_count, uploaded_info, errors = self._save_uploaded_files(files, full_target_dir)
            
            # 改进错误处理逻辑
            if uploaded_count == 0 and errors:
                # 所有文件都上传失败
                return {
                    'success': False,
                    'message': f'所有文件上传失败',
                    'errors': errors,
                    'total_uploaded': 0
                }
            elif uploaded_count > 0 and errors:
                # 部分文件上传成功，部分失败
                return {
                    'success': True,
                    'message': f'成功上传 {uploaded_count} 个文件，{len(errors)} 个文件失败',
                    'files': uploaded_info,
                    'errors': errors,
                    'total_uploaded': uploaded_count
                }
            else:
                # 所有文件都上传成功
                return {
                    'success': True,
                    'message': f'成功上传 {uploaded_count} 个文件',
                    'files': uploaded_info,
                    'total_uploaded': uploaded_count
                }
                
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def _save_uploaded_files(self, files, target_directory):
        """保存上传的文件并返回上传结果"""
        uploaded_count = 0
        uploaded_info = []
        errors = []
        
        for file in files:
            logger.info(f"处理文件: {file.filename}")
            if file.filename == '':
                logger.warning("跳过空文件名")
                continue
            
            # 验证文件扩展名
            logger.info(f"验证文件扩展名: {file.filename}")
            is_valid, message = self.security_service.validate_file_extension(file.filename)
            if not is_valid:
                logger.warning(f"文件扩展名验证失败: {file.filename} - {message}")
                errors.append(f"{file.filename}: {message}")
                continue
            
            # 验证文件大小
            if hasattr(self.config, 'MAX_FILE_SIZE'):
                # 获取文件大小，兼容不同的Flask版本
                file_size = getattr(file, 'content_length', None)
                if file_size is None:
                    # 如果没有content_length，尝试从文件流获取
                    try:
                        file.seek(0, 2)  # 移动到文件末尾
                        file_size = file.tell()
                        file.seek(0)  # 重置到文件开头
                    except:
                        file_size = 0
                
                if file_size and file_size > self.config.MAX_FILE_SIZE:
                    errors.append(f"{file.filename}: 文件大小超过限制 ({file_size} > {self.config.MAX_FILE_SIZE})")
                    continue
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(target_directory, filename)
            
            # 检查文件是否已存在，如果存在则重命名
            counter = 1
            original_filename = filename
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                file_path = os.path.join(target_directory, filename)
                counter += 1
            
            try:
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                logger.info(f"文件上传成功: {filename}, 大小: {file_size} 字节")
                
                uploaded_count += 1
                uploaded_info.append({
                    'name': filename,
                    'path': os.path.relpath(file_path, start=self.config.ROOT_DIR).replace('\\', '/'),
                    'size': file_size,
                    'md5': hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                })
            except Exception as e:
                errors.append(f"{file.filename}: 保存失败 - {str(e)}")
                logger.error(f"文件保存失败: {file.filename}, 错误: {str(e)}")
        
        return uploaded_count, uploaded_info, errors
