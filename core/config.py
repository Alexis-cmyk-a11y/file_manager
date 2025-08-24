"""
文件管理系统配置模块
提供应用的所有配置选项
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """应用配置类"""
    
    def __init__(self):
        # 根目录配置（使用当前目录）
        self.ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 从环境变量和配置文件加载配置
        self._load_environment_config()
        self._load_config_file()
        
        # 验证配置
        self._validate_config()
    
    def _load_environment_config(self):
        """从环境变量加载配置"""
        # 文件大小限制
        self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 10 * 1024 * 1024 * 1024))  # 1GB
        self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024 * 1024))  # 1GB单文件限制

        # 文件类型控制
        # 允许上传的文件类型（设置为空集合表示允许所有类型）
        self.ALLOWED_EXTENSIONS = set()
        
        # 禁止的文件扩展名
        forbidden_exts = os.getenv('FORBIDDEN_EXTENSIONS', '.com,.pif,.app')
        self.FORBIDDEN_EXTENSIONS = set(ext.strip() for ext in forbidden_exts.split(',') if ext.strip())
        
        # 是否允许上传可执行文件
        self.ALLOW_EXECUTABLE_FILES = os.getenv('ALLOW_EXECUTABLE_FILES', 'false').lower() == 'true'
        
        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 支持 'json' 或传统格式
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/file_manager.log')
        self.LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
        self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 30))  # 保留30天的日志
        
        # 高级日志配置
        self.LOG_ENABLE_CONSOLE = os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true'
        self.LOG_ENABLE_FILE = os.getenv('LOG_ENABLE_FILE', 'true').lower() == 'true'
        self.LOG_ENABLE_JSON = os.getenv('LOG_ENABLE_JSON', 'true').lower() == 'true'
        self.LOG_ENABLE_COLOR = os.getenv('LOG_ENABLE_COLOR', 'true').lower() == 'true'
        self.LOG_ROTATION_WHEN = os.getenv('LOG_ROTATION_WHEN', 'midnight')  # midnight, hour, day
        self.LOG_ROTATION_INTERVAL = int(os.getenv('LOG_ROTATION_INTERVAL', 1))
        self.LOG_COMPRESS_OLD = os.getenv('LOG_COMPRESS_OLD', 'true').lower() == 'true'

        # 界面配置
        self.APP_NAME = os.getenv('APP_NAME', "文件管理系统")
        self.THEME_COLOR = os.getenv('THEME_COLOR', "#4a6fa5")
        self.SECONDARY_COLOR = os.getenv('SECONDARY_COLOR', "#6c8ebf")

        # 安全配置
        self.SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
        self.ENABLE_DOWNLOAD = os.getenv('ENABLE_DOWNLOAD', 'true').lower() == 'true'
        self.ENABLE_DELETE = os.getenv('ENABLE_DELETE', 'true').lower() == 'true'
        self.ENABLE_UPLOAD = os.getenv('ENABLE_UPLOAD', 'true').lower() == 'true'
        self.ENABLE_CREATE_FOLDER = os.getenv('ENABLE_CREATE_FOLDER', 'true').lower() == 'true'
        self.ENABLE_RENAME = os.getenv('ENABLE_RENAME', 'true').lower() == 'true'
        self.ENABLE_MOVE_COPY = os.getenv('ENABLE_MOVE_COPY', 'true').lower() == 'true'
        self.ENABLE_FILE_OPS = os.getenv('ENABLE_FILE_OPS', 'true').lower() == 'true'

        # 安全限制
        self.RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per minute')  # 速率限制
        self.SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 会话超时时间(秒)

        # Flask服务器配置
        self.SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
        self.SERVER_PORT = int(os.getenv('SERVER_PORT', 8888))
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD', 'false').lower() == 'true'

        # 静态文件配置
        self.STATIC_VERSION = os.getenv('STATIC_VERSION', '1.0.0')
        self.SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv('SEND_FILE_MAX_AGE_DEFAULT', 3600))
        self.STATIC_COMPRESS = os.getenv('STATIC_COMPRESS', 'true').lower() == 'true'

        # 前端资源配置
        self.FRONTEND_CONFIG = {
            'app_name': os.getenv('FRONTEND_APP_NAME', '文件管理系统'),
            'default_view': os.getenv('FRONTEND_DEFAULT_VIEW', 'list'),
            'page_size': int(os.getenv('FRONTEND_PAGE_SIZE', 20)),
            'show_hidden': os.getenv('FRONTEND_SHOW_HIDDEN', 'false').lower() == 'true',
            'enable_drag_drop': os.getenv('FRONTEND_ENABLE_DRAG_DROP', 'true').lower() == 'true',
            'enable_preview': os.getenv('FRONTEND_ENABLE_PREVIEW', 'true').lower() == 'true'
        }

        # 细粒度权限控制
        self.PERMISSIONS = {
            'upload': os.getenv('PERMISSION_UPLOAD', 'true').lower() == 'true',
            'download': os.getenv('PERMISSION_DOWNLOAD', 'true').lower() == 'true',
            'delete': os.getenv('PERMISSION_DELETE', 'true').lower() == 'true',
            'rename': os.getenv('PERMISSION_RENAME', 'true').lower() == 'true',
            'create_folder': os.getenv('PERMISSION_CREATE_FOLDER', 'true').lower() == 'true',
            'admin_ops': os.getenv('PERMISSION_ADMIN_OPS', 'false').lower() == 'true'
        }

        # 开发/生产环境配置
        self.ENV = os.getenv('ENV', 'production')
        
        # Redis配置
        self.REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        self.REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
        self.REDIS_DB = int(os.getenv('REDIS_DB', 0))
        self.REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
        self.REDIS_SSL = os.getenv('REDIS_SSL', 'false').lower() == 'true'
        
        # 高级Redis配置
        self.REDIS_POOL_CONFIG = {
            'max_connections': int(os.getenv('REDIS_MAX_CONNECTIONS', 20)),
            'retry_on_timeout': os.getenv('REDIS_RETRY_ON_TIMEOUT', 'true').lower() == 'true',
            'socket_keepalive': os.getenv('REDIS_SOCKET_KEEPALIVE', 'true').lower() == 'true',
            'health_check_interval': int(os.getenv('REDIS_HEALTH_CHECK_INTERVAL', 30))
        }
        
        # 缓存配置
        self.CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', 300))  # 5分钟
        self.CACHE_MAX_ITEMS = int(os.getenv('CACHE_MAX_ITEMS', 10000))
        
        # 性能配置
        self.ENABLE_PERFORMANCE_MONITORING = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
        self.PERFORMANCE_SLOW_THRESHOLD = float(os.getenv('PERFORMANCE_SLOW_THRESHOLD', 1.0))  # 秒
        
        # 安全增强配置
        self.ENABLE_SECURITY_LOGGING = os.getenv('ENABLE_SECURITY_LOGGING', 'true').lower() == 'true'
        self.SECURITY_LOG_LEVEL = os.getenv('SECURITY_LOG_LEVEL', 'WARNING')
        self.MAX_PATH_LENGTH = int(os.getenv('MAX_PATH_LENGTH', 4096))
        self.ENABLE_FILE_TYPE_DETECTION = os.getenv('ENABLE_FILE_TYPE_DETECTION', 'true').lower() == 'true'
    
    def _load_config_file(self):
        """从配置文件加载配置"""
        config_files = [
            'config.yaml',
            'config.yml',
            'config.json',
            os.path.expanduser('~/.file_manager/config.yaml'),
            os.path.expanduser('~/.file_manager/config.yml'),
            '/etc/file_manager/config.yaml',
            '/etc/file_manager/config.yml'
        ]
        
        for config_file in config_files:
            if self._try_load_config_file(config_file):
                break
    
    def _try_load_config_file(self, config_file: str) -> bool:
        """尝试加载配置文件"""
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                return False
            
            # 根据文件扩展名选择加载方式
            if config_path.suffix in ['.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            elif config_path.suffix == '.json':
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                return False
            
            # 应用配置文件中的设置
            self._apply_config_data(config_data)
            
            print(f"✅ 已加载配置文件: {config_file}")
            return True
            
        except Exception as e:
            print(f"⚠️  加载配置文件失败: {config_file}, 错误: {e}")
            return False
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """应用配置文件数据"""
        if not config_data:
            return
        
        # 环境特定配置
        env = self.ENV
        if env in config_data:
            env_config = config_data[env]
            self._apply_config_data(env_config)
        
        # 应用通用配置
        for key, value in config_data.items():
            if hasattr(self, key):
                # 对于复杂类型，需要特殊处理
                if key == 'FRONTEND_CONFIG' and isinstance(value, dict):
                    self.FRONTEND_CONFIG.update(value)
                elif key == 'PERMISSIONS' and isinstance(value, dict):
                    self.PERMISSIONS.update(value)
                elif key == 'REDIS_POOL_CONFIG' and isinstance(value, dict):
                    self.REDIS_POOL_CONFIG.update(value)
                else:
                    setattr(self, key, value)
    
    def _validate_config(self):
        """验证配置的有效性"""
        errors = []
        
        # 验证端口范围
        if not (1 <= self.SERVER_PORT <= 65535):
            errors.append(f"服务器端口必须在1-65535之间: {self.SERVER_PORT}")
        
        # 验证文件大小限制
        if self.MAX_FILE_SIZE <= 0:
            errors.append("文件大小限制必须大于0")
        
        # 验证日志级别
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL not in valid_log_levels:
            errors.append(f"无效的日志级别: {self.LOG_LEVEL}")
        
        # 验证Redis配置
        if not (1 <= self.REDIS_PORT <= 65535):
            errors.append(f"Redis端口必须在1-65535之间: {self.REDIS_PORT}")
        
        # 验证缓存配置
        if self.CACHE_DEFAULT_TTL <= 0:
            errors.append("缓存TTL必须大于0")
        
        # 如果有错误，抛出异常
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return getattr(self, key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        config_dict = {}
        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):
                value = getattr(self, key)
                if not key.startswith('__'):
                    config_dict[key] = value
        return config_dict
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        return {
            'environment': self.ENV,
            'debug_mode': self.DEBUG_MODE,
            'server_host': self.SERVER_HOST,
            'server_port': self.SERVER_PORT,
            'redis_connected': self.REDIS_HOST != 'localhost' or self.REDIS_PORT != 6379,
            'cache_enabled': self.CACHE_ENABLED,
            'performance_monitoring': self.ENABLE_PERFORMANCE_MONITORING,
            'security_logging': self.ENABLE_SECURITY_LOGGING
        }
    
    def reload(self):
        """重新加载配置"""
        self._load_environment_config()
        self._load_config_file()
        self._validate_config()
        print("✅ 配置已重新加载")
    
    def print_config_summary(self):
        """打印配置摘要"""
        print("\n📋 配置摘要:")
        print(f"   🌍 环境: {self.ENV}")
        print(f"   🚀 服务器: {self.SERVER_HOST}:{self.SERVER_PORT}")
        print(f"   🐛 调试模式: {'开启' if self.DEBUG_MODE else '关闭'}")
        print(f"   💾 Redis: {self.REDIS_HOST}:{self.REDIS_PORT}")
        print(f"   📁 根目录: {self.ROOT_DIR}")
        print(f"   📏 最大文件大小: {self.MAX_FILE_SIZE / (1024*1024*1024):.1f}GB")
        print(f"   🔒 安全日志: {'开启' if self.ENABLE_SECURITY_LOGGING else '关闭'}")
        print(f"   📊 性能监控: {'开启' if self.ENABLE_PERFORMANCE_MONITORING else '关闭'}")
        print()

# 创建默认配置实例
config = Config()

# 导出配置类
__all__ = ['Config', 'config']
