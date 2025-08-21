"""
API路由模块
包含所有API端点的路由定义
"""

from . import file_ops, upload, download, system

__all__ = ['file_ops', 'upload', 'download', 'system']
