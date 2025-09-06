"""
在线编辑器服务
提供文件读取、保存、语法高亮等功能
"""

import os
import mimetypes
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from utils.logger import get_logger

class EditorService:
    """在线编辑器服务类"""
    
    def __init__(self, root_dir: str = None):
        """初始化编辑器服务"""
        self.root_dir = root_dir or os.getcwd()
        self.logger = get_logger(__name__)
        
        # 支持编辑的文件类型
        self.editable_extensions = {
            # 文本文件
            '.txt', '.md', '.rst', '.log',
            # 代码文件
            '.py', '.js', '.ts', '.html', '.css', '.scss', '.sass',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php',
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.sql', '.xml', '.json', '.yaml', '.yml', '.toml',
            '.ini', '.cfg', '.conf', '.env',
            # 配置文件
            '.gitignore', '.dockerignore', '.editorconfig',
            '.eslintrc', '.prettierrc', '.babelrc',
            # 其他文本格式
            '.csv', '.tsv', '.tex', '.bib'
        }
        
        # 文件类型对应的语法高亮模式
        self.syntax_modes = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'xml',
            '.css': 'css',
            '.scss': 'css',
            '.sass': 'css',
            '.java': 'clike',
            '.cpp': 'clike',
            '.c': 'clike',
            '.h': 'clike',
            '.hpp': 'clike',
            '.cs': 'clike',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sql': 'sql',
            '.xml': 'xml',
            '.json': 'javascript',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.md': 'markdown',
            '.rst': 'rst',
            '.tex': 'latex',
            '.csv': 'csv',
            '.tsv': 'csv'
        }
    
    def can_edit_file(self, file_path: str) -> bool:
        """检查文件是否可以编辑"""
        try:
            # 检查文件扩展名
            ext = Path(file_path).suffix.lower()
            if ext in self.editable_extensions:
                return True
            
            # 检查MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type.startswith('text/'):
                return True
                
            return False
        except Exception as e:
            self.logger.error(f"检查文件可编辑性失败: {str(e)}")
            return False
    
    def get_syntax_mode(self, file_path: str) -> str:
        """获取文件的语法高亮模式"""
        try:
            ext = Path(file_path).suffix.lower()
            return self.syntax_modes.get(ext, 'text')
        except Exception:
            return 'text'
    
    def read_file_content(self, file_path: str) -> Dict[str, any]:
        """读取文件内容"""
        try:
            # 如果已经是绝对路径，直接使用
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                # 处理共享文件路径
                if '_shared/' in file_path:
                    # 共享文件路径格式：owner_shared/filename
                    abs_path = os.path.join(self.root_dir, 'home', 'shared', file_path)
                else:
                    abs_path = os.path.join(self.root_dir, file_path)
            
            # 安全检查：确保文件路径在系统根目录内
            try:
                from core.config import config
                system_root = config.FILESYSTEM_ROOT
                if not os.path.abspath(abs_path).startswith(os.path.abspath(system_root)):
                    raise ValueError("文件路径超出允许范围")
            except:
                # 如果无法获取配置，使用默认检查
                if not os.path.abspath(abs_path).startswith(os.path.abspath(self.root_dir)):
                    raise ValueError("文件路径超出允许范围")
            
            if not os.path.exists(abs_path):
                raise FileNotFoundError("文件不存在")
            
            if not os.path.isfile(abs_path):
                raise ValueError("指定路径不是文件")
            
            # 检查文件大小（限制为10MB）
            file_size = os.path.getsize(abs_path)
            if file_size > 10 * 1024 * 1024:  # 10MB
                raise ValueError("文件过大，无法编辑")
            
            # 读取文件内容
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 获取文件信息
            file_info = {
                'success': True,
                'content': content,
                'encoding': 'utf-8',
                'size': file_size,
                'syntax_mode': self.get_syntax_mode(file_path),
                'line_count': len(content.splitlines()),
                'path': file_path,
                'name': os.path.basename(file_path)
            }
            
            return file_info
            
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(abs_path, 'r', encoding='gbk') as f:
                    content = f.read()
                
                return {
                    'success': True,
                    'content': content,
                    'encoding': 'gbk',
                    'size': os.path.getsize(abs_path),
                    'syntax_mode': self.get_syntax_mode(file_path),
                    'line_count': len(content.splitlines()),
                    'path': file_path,
                    'name': os.path.basename(file_path)
                }
            except Exception:
                raise ValueError("文件编码不支持")
                
        except Exception as e:
            self.logger.error(f"读取文件失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def save_file_content(self, file_path: str, content: str) -> Dict[str, any]:
        """保存文件内容"""
        try:
            # 检查是否为共享文件（共享文件不允许编辑）
            if '_shared/' in file_path:
                return {
                    'success': False,
                    'message': '共享文件不允许编辑'
                }
            
            # 如果已经是绝对路径，直接使用
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                abs_path = os.path.join(self.root_dir, file_path)
            
            # 安全检查：确保文件路径在系统根目录内
            try:
                from core.config import config
                system_root = config.FILESYSTEM_ROOT
                if not os.path.abspath(abs_path).startswith(os.path.abspath(system_root)):
                    raise ValueError("文件路径超出允许范围")
            except:
                # 如果无法获取配置，使用默认检查
                if not os.path.abspath(abs_path).startswith(os.path.abspath(self.root_dir)):
                    raise ValueError("文件路径超出允许范围")
            
            # 创建目录（如果不存在）
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            
            # 备份原文件（如果存在）
            backup_path = None
            if os.path.exists(abs_path):
                backup_path = f"{abs_path}.backup"
                try:
                    import shutil
                    shutil.copy2(abs_path, backup_path)
                except Exception as e:
                    self.logger.warning(f"创建备份失败: {str(e)}")
            
            # 保存文件内容
            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 获取更新后的文件信息
            file_info = {
                'success': True,
                'message': '文件保存成功',
                'path': file_path,
                'size': len(content.encode('utf-8')),
                'line_count': len(content.splitlines()),
                'backup_path': backup_path
            }
            
            self.logger.info(f"文件保存成功: {file_path}")
            return file_info
            
        except Exception as e:
            self.logger.error(f"保存文件失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_file_preview(self, file_path: str, max_lines: int = 100) -> Dict[str, any]:
        """获取文件预览（前几行）"""
        try:
            # 如果已经是绝对路径，直接使用
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                # 处理共享文件路径
                if '_shared/' in file_path:
                    # 共享文件路径格式：owner_shared/filename
                    abs_path = os.path.join(self.root_dir, 'home', 'shared', file_path)
                else:
                    abs_path = os.path.join(self.root_dir, file_path)
            
            if not os.path.exists(abs_path):
                raise FileNotFoundError("文件不存在")
            
            if not os.path.isfile(abs_path):
                raise ValueError("指定路径不是文件")
            
            # 读取前几行
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip('\n'))
            
            content = '\n'.join(lines)
            truncated = len(lines) >= max_lines
            
            return {
                'success': True,
                'content': content,
                'truncated': truncated,
                'line_count': len(lines),
                'total_lines': len(lines) if not truncated else '未知',
                'syntax_mode': self.get_syntax_mode(file_path)
            }
            
        except Exception as e:
            self.logger.error(f"获取文件预览失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def search_in_file(self, file_path: str, search_term: str, case_sensitive: bool = False) -> Dict[str, any]:
        """在文件中搜索文本"""
        try:
            # 如果已经是绝对路径，直接使用
            if os.path.isabs(file_path):
                abs_path = file_path
            else:
                # 处理共享文件路径
                if '_shared/' in file_path:
                    # 共享文件路径格式：owner_shared/filename
                    abs_path = os.path.join(self.root_dir, 'home', 'shared', file_path)
                else:
                    abs_path = os.path.join(self.root_dir, file_path)
            
            if not os.path.exists(abs_path):
                raise FileNotFoundError("文件不存在")
            
            if not os.path.isfile(abs_path):
                raise ValueError("指定路径不是文件")
            
            matches = []
            with open(abs_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not case_sensitive:
                        if search_term.lower() in line.lower():
                            matches.append({
                                'line': line_num,
                                'content': line.rstrip('\n'),
                                'column': line.lower().find(search_term.lower()) + 1
                            })
                    else:
                        if search_term in line:
                            matches.append({
                                'line': line_num,
                                'content': line.rstrip('\n'),
                                'column': line.find(search_term) + 1
                            })
            
            return {
                'success': True,
                'matches': matches,
                'total_matches': len(matches),
                'search_term': search_term,
                'case_sensitive': case_sensitive
            }
            
        except Exception as e:
            self.logger.error(f"文件搜索失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
