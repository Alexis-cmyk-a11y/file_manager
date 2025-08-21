"""
文件管理系统核心模块
提供应用的核心功能和配置
"""

from .config import Config
from .app import create_app

__version__ = "2.0.0"
__author__ = "File Manager System"

__all__ = ['Config', 'create_app']
