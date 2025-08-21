"""
系统信息服务
提供系统状态、配置信息等
"""

import os
import sys
import logging

from core.config import Config

logger = logging.getLogger(__name__)

class SystemService:
    """系统信息服务类"""
    
    def __init__(self):
        self.config = Config()
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            # 尝试导入psutil获取更详细的系统信息
            try:
                import psutil
                
                # 获取磁盘使用情况
                disk_usage = psutil.disk_usage(self.config.ROOT_DIR)
                
                # 获取内存使用情况
                memory = psutil.virtual_memory()
                
                system_info = {
                    'success': True,
                    'system': {
                        'platform': sys.platform,
                        'python_version': sys.version,
                        'root_directory': self.config.ROOT_DIR
                    },
                    'storage': {
                        'total': disk_usage.total,
                        'used': disk_usage.used,
                        'free': disk_usage.free,
                        'percent': disk_usage.percent
                    },
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent
                    },
                    'config': {
                        'app_name': self.config.APP_NAME,
                        'version': '2.0.0',
                        'environment': self.config.ENV
                    }
                }
                
                return system_info
                
            except ImportError:
                # 如果没有psutil，返回基本信息
                return {
                    'success': True,
                    'system': {
                        'platform': sys.platform,
                        'python_version': sys.version,
                        'root_directory': self.config.ROOT_DIR
                    },
                    'config': {
                        'app_name': self.config.APP_NAME,
                        'version': '2.0.0',
                        'environment': self.config.ENV
                    },
                    'note': '安装 psutil 包可获取更详细的系统信息'
                }
                
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {'success': False, 'message': str(e)}
