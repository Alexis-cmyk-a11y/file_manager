"""
文件管理系统配置模块
提供应用的所有配置选项
"""

import os

class Config:
    """应用配置类"""
    
    # 根目录配置（使用当前目录）
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 上传文件大小限制（单位：字节，默认100MB）
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024 * 1024  # 1GB
    MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024  # 1GB单文件限制

    # 文件类型控制
    # 允许上传的文件类型（设置为空集合表示允许所有类型）
    ALLOWED_EXTENSIONS = set()
    
    # 禁止的文件扩展名
    FORBIDDEN_EXTENSIONS = {'.com', '.pif', '.app'}
    
    # 是否允许上传可执行文件
    ALLOW_EXECUTABLE_FILES = False
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = 'json'  # 支持 'json' 或传统格式
    LOG_FILE = 'logs/file_manager.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 30  # 保留30天的日志
    
    # 高级日志配置
    LOG_ENABLE_CONSOLE = True
    LOG_ENABLE_FILE = True
    LOG_ENABLE_JSON = True
    LOG_ENABLE_COLOR = True
    LOG_ROTATION_WHEN = 'midnight'  # midnight, hour, day
    LOG_ROTATION_INTERVAL = 1
    LOG_COMPRESS_OLD = True

    # 界面配置
    APP_NAME = "文件管理系统"
    THEME_COLOR = "#4a6fa5"
    SECONDARY_COLOR = "#6c8ebf"

    # 安全配置
    SECRET_KEY = os.urandom(24).hex()
    ENABLE_DOWNLOAD = True
    ENABLE_DELETE = True
    ENABLE_UPLOAD = True
    ENABLE_CREATE_FOLDER = True
    ENABLE_RENAME = True
    ENABLE_MOVE_COPY = True
    ENABLE_FILE_OPS = True

    # 安全限制
    RATE_LIMIT = '100 per minute'  # 速率限制
    SESSION_TIMEOUT = 3600  # 会话超时时间(秒)

    # Flask服务器配置
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 8888
    DEBUG_MODE = False
    TEMPLATES_AUTO_RELOAD = False

    # 静态文件配置
    STATIC_VERSION = '1.0.0'
    SEND_FILE_MAX_AGE_DEFAULT = 3600
    STATIC_COMPRESS = True

    # 前端资源配置
    FRONTEND_CONFIG = {
        'app_name': '文件管理系统',
        'default_view': 'list',
        'page_size': 20,
        'show_hidden': False,
        'enable_drag_drop': True,
        'enable_preview': True
    }

    # 细粒度权限控制
    PERMISSIONS = {
        'upload': True,
        'download': True,
        'delete': True,
        'rename': True,
        'create_folder': True,
        'admin_ops': False
    }

    # 开发/生产环境配置
    ENV = 'production'
    
    # Redis配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    REDIS_SSL = False
    REDIS_SSL_CERT_REQS = 'none'
    REDIS_CONNECTION_POOL_SIZE = 10
    REDIS_SOCKET_TIMEOUT = 5
    REDIS_SOCKET_CONNECT_TIMEOUT = 5
    REDIS_RETRY_ON_TIMEOUT = True
    REDIS_HEALTH_CHECK_INTERVAL = 30
    
    @classmethod
    def is_production(cls):
        return cls.ENV == 'production'
    
    @classmethod
    def is_development(cls):
        return cls.ENV == 'development'
    
    def __init__(self):
        # 生产环境自动调整配置
        if self.is_production():
            self.DEBUG_MODE = False
            self.TEMPLATES_AUTO_RELOAD = False
            self.STATIC_COMPRESS = True
            self.LOG_LEVEL = 'WARNING'
        
        # 确保日志文件路径是绝对路径
        self._setup_log_file_path()
    
    def _setup_log_file_path(self):
        """确保日志文件路径是绝对路径"""
        if not os.path.isabs(self.LOG_FILE):
            # 如果是相对路径，则相对于项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.LOG_FILE = os.path.normpath(os.path.join(project_root, self.LOG_FILE))
