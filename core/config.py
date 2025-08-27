"""
文件管理系统配置模块
提供应用的所有配置选项，使用配置文件而不是环境变量
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from core.config_manager import config_manager, ConfigManager

class Config:
    """应用配置类 - 兼容旧版本的配置接口"""
    
    def __init__(self):
        # 根目录配置
        self.ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 使用新的配置管理器
        self.config_manager = config_manager
        
        # 加载配置
        self._load_config()
        
        # 验证配置
        self._validate_config()
    
    def _load_config(self):
        """从配置管理器加载配置"""
        # 应用配置 - 从配置文件直接获取
        self.APP_NAME = self.config_manager.get('app.name', '文件管理系统')
        self.VERSION = self.config_manager.get('app.version', '2.0.0')
        self.DESCRIPTION = self.config_manager.get('app.description', '现代化的文件管理系统')
        
        # 服务器配置
        server_config = self.config_manager.get_server_config()
        self.SERVER_HOST = server_config.host
        self.SERVER_PORT = server_config.port
        self.DEBUG_MODE = server_config.debug
        
        # 环境配置
        env_config = self.config_manager.get_environment_config()
        self.ENV = self.config_manager.environment
        self.LOG_LEVEL = env_config.get('log_level', 'INFO')
        
        # 功能配置
        features = env_config.get('features', {})
        self.ENABLE_PERFORMANCE_MONITORING = features.get('enable_performance_monitoring', True)
        self.ENABLE_SECURITY_LOGGING = features.get('enable_security_logging', True)
        self.ENABLE_CACHE = features.get('enable_cache', True)
        self.ENABLE_COMPRESSION = features.get('enable_compression', True)
        
        # 限制配置
        limits = env_config.get('limits', {})
        self.MAX_FILE_SIZE = limits.get('max_file_size', 1073741824)  # 1GB
        self.MAX_UPLOAD_FILES = limits.get('max_upload_files', 100)
        self.MAX_PATH_LENGTH = limits.get('max_path_length', 4096)
        
        # 数据库配置
        db_config = self.config_manager.get_database_config()
        mysql_config = db_config.mysql
        self.MYSQL_HOST = mysql_config.get('host', 'localhost')
        self.MYSQL_PORT = mysql_config.get('port', 3306)
        self.MYSQL_DATABASE = mysql_config.get('database', 'file_manager')
        self.MYSQL_USERNAME = mysql_config.get('username', 'root')
        self.MYSQL_PASSWORD = mysql_config.get('password', '')
        self.MYSQL_CHARSET = mysql_config.get('charset', 'utf8mb4')
        self.MYSQL_POOL_CONFIG = mysql_config.get('pool', {})
        self.MYSQL_OPTIONS = mysql_config.get('options', {})
        self.MYSQL_LOG_RETENTION = mysql_config.get('maintenance', {})
        
        redis_config = db_config.redis
        self.REDIS_HOST = redis_config.get('host', 'localhost')
        self.REDIS_PORT = redis_config.get('port', 6379)
        self.REDIS_DB = redis_config.get('db', 0)
        self.REDIS_PASSWORD = redis_config.get('password')
        self.REDIS_SSL = redis_config.get('ssl', False)
        self.REDIS_POOL_CONFIG = redis_config.get('pool', {})
        
        # 安全配置
        security_config = self.config_manager.get_security_config()
        self.SECRET_KEY = security_config.secret_key or os.urandom(24).hex()
        self.SESSION_TIMEOUT = security_config.session_timeout
        self.RATE_LIMIT = security_config.rate_limit
        self.JWT_EXPIRATION = security_config.jwt_expiration
        self.PASSWORD_POLICY = security_config.password_policy
        self.FILE_VALIDATION = security_config.file_validation
        
        # 日志配置
        logging_config = self.config_manager.get_logging_config()
        self.LOG_LEVEL = logging_config.level
        self.LOG_FORMAT = logging_config.format
        self.LOG_FILE = logging_config.file
        self.LOG_MAX_SIZE = logging_config.max_size
        self.LOG_BACKUP_COUNT = logging_config.backup_count
        self.LOG_ENABLE_CONSOLE = logging_config.console.get('enabled', True)
        self.LOG_ENABLE_FILE = logging_config.file_config.get('enabled', True)
        self.LOG_ENABLE_JSON = logging_config.json.get('enabled', True)
        self.LOG_ENABLE_COLOR = logging_config.console.get('colored', True)
        
        # 缓存配置
        cache_config = self.config_manager.get_cache_config()
        self.CACHE_ENABLED = cache_config.enabled
        self.CACHE_DEFAULT_TTL = cache_config.default_ttl
        self.CACHE_MAX_ITEMS = cache_config.max_items
        self.CACHE_STRATEGIES = cache_config.strategies
        
        # 前端配置
        frontend_config = self.config_manager.get_frontend_config()
        self.FRONTEND_CONFIG = {
            'app_name': frontend_config.app_name,
            'theme': frontend_config.theme,
            'features': frontend_config.features,
            'editor': frontend_config.editor,
            'notifications': frontend_config.notifications
        }
        
        # 文件系统配置
        filesystem_config = self.config_manager.get_filesystem_config()
        self.FILESYSTEM_ROOT = filesystem_config.root_directory or self.ROOT_DIR
        self.UPLOAD_CONFIG = filesystem_config.upload
        self.DOWNLOAD_CONFIG = filesystem_config.download
        self.PREVIEW_CONFIG = filesystem_config.preview
        
        # 性能配置
        performance_config = self.config_manager.get_performance_config()
        self.PERFORMANCE_MONITORING = performance_config.monitoring_enabled
        self.SLOW_THRESHOLD = performance_config.slow_threshold
        self.METRICS_RETENTION = performance_config.metrics_retention
        
        # 监控配置
        monitoring_config = self.config_manager.get_monitoring_config()
        self.HEALTH_CHECK_ENABLED = monitoring_config.health_check.get('enabled', True)
        self.HEALTH_CHECK_INTERVAL = monitoring_config.health_check.get('interval', 30)
        self.METRICS_ENABLED = monitoring_config.metrics.get('enabled', True)
        self.ALERTS_ENABLED = monitoring_config.alerts.get('enabled', True)
        
        # 国际化配置
        self.I18N_CONFIG = {
            'default_language': self.config_manager.get('i18n.default_language', 'zh-CN'),
            'supported_languages': self.config_manager.get('i18n.supported_languages', ['zh-CN', 'en-US']),
            'timezone': self.config_manager.get('i18n.timezone', 'Asia/Shanghai')
        }
        
        # 备份配置
        self.BACKUP_CONFIG = {
            'enabled': self.config_manager.get('backup.enabled', False),
            'schedule': self.config_manager.get('backup.schedule', '0 2 * * *'),
            'retention': self.config_manager.get('backup.retention', 7)
        }
        
        # 邮件配置
        self.EMAIL_CONFIG = {
            'enabled': self.config_manager.get('email.enabled', False),
            'smtp': self.config_manager.get('email.smtp', {}),
            'templates': self.config_manager.get('email.templates', {})
        }
    
    def _validate_config(self):
        """验证配置的有效性"""
        # 基本验证
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY 不能为空")
        
        if not (1 <= self.SERVER_PORT <= 65535):
            raise ValueError(f"服务器端口必须在1-65535之间: {self.SERVER_PORT}")
        
        if self.MAX_FILE_SIZE <= 0:
            raise ValueError("最大文件大小必须大于0")
        
        if self.MAX_PATH_LENGTH <= 0:
            raise ValueError("最大路径长度必须大于0")
        
        # 数据库配置验证
        if not self.MYSQL_HOST:
            raise ValueError("MySQL主机不能为空")
        
        if not (1 <= self.MYSQL_PORT <= 65535):
            raise ValueError(f"MySQL端口必须在1-65535之间: {self.MYSQL_PORT}")
        
        if not self.MYSQL_DATABASE:
            raise ValueError("MySQL数据库名不能为空")
        
        # Redis配置验证
        if not self.REDIS_HOST:
            raise ValueError("Redis主机不能为空")
        
        if not (1 <= self.REDIS_PORT <= 65535):
            raise ValueError(f"Redis端口必须在1-65535之间: {self.REDIS_PORT}")
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        password = f":{self.MYSQL_PASSWORD}@" if self.MYSQL_PASSWORD else "@"
        return f"mysql+pymysql://{self.MYSQL_USERNAME}{password}{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset={self.MYSQL_CHARSET}"
    
    def get_redis_url(self) -> str:
        """获取Redis连接URL"""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        protocol = "rediss://" if self.REDIS_SSL else "redis://"
        return f"{protocol}{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def reload_config(self):
        """重新加载配置"""
        if self.config_manager.reload_config():
            self._load_config()
            self._validate_config()
            return True
        return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            'app_name': self.APP_NAME,
            'version': self.VERSION,
            'environment': self.ENV,
            'debug_mode': self.DEBUG_MODE,
            'server': {
                'host': self.SERVER_HOST,
                'port': self.SERVER_PORT
            },
            'database': {
                'mysql_host': self.MYSQL_HOST,
                'mysql_port': self.MYSQL_PORT,
                'mysql_database': self.MYSQL_DATABASE,
                'redis_host': self.REDIS_HOST,
                'redis_port': self.REDIS_PORT
            },
            'features': {
                'performance_monitoring': self.ENABLE_PERFORMANCE_MONITORING,
                'security_logging': self.ENABLE_SECURITY_LOGGING,
                'cache': self.CACHE_ENABLED,
                'compression': self.ENABLE_COMPRESSION
            },
            'limits': {
                'max_file_size': self.MAX_FILE_SIZE,
                'max_upload_files': self.MAX_UPLOAD_FILES,
                'max_path_length': self.MAX_PATH_LENGTH
            }
        }
    
    def export_config(self, format: str = 'json') -> str:
        """导出配置"""
        return self.config_manager.export_config(format)
    
    def validate_config_file(self, config_file: str) -> bool:
        """验证配置文件"""
        return self.config_manager.validate_config_file(config_file)

# 创建全局配置实例
config = Config()
