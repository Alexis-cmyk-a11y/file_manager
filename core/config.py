"""
文件管理系统配置模块
提供应用的所有配置选项
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 根目录配置（使用当前目录）
    ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 如果环境变量设置的是无效路径，则使用当前目录
    if ROOT_DIR == '/path/to/your/files' or not os.path.exists(ROOT_DIR):
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 上传文件大小限制（单位：字节，默认50GB）
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024 * 1024))

    # 允许上传的文件类型（设置为空集合表示允许所有类型）
    ALLOWED_EXTENSIONS = set()

    # 禁止的文件扩展名
    FORBIDDEN_EXTENSIONS = {'.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar'}
    
    # 是否允许上传可执行文件
    ALLOW_EXECUTABLE_FILES = os.getenv('ALLOW_EXECUTABLE_FILES', 'false').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 支持 'json' 或传统格式
    LOG_FILE = os.getenv('LOG_FILE', 'logs/file_manager.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 30))  # 保留30天的日志
    
    # 高级日志配置
    LOG_ENABLE_CONSOLE = os.getenv('LOG_ENABLE_CONSOLE', 'true').lower() == 'true'
    LOG_ENABLE_FILE = os.getenv('LOG_ENABLE_FILE', 'true').lower() == 'true'
    LOG_ENABLE_JSON = os.getenv('LOG_ENABLE_JSON', 'true').lower() == 'true'
    LOG_ENABLE_COLOR = os.getenv('LOG_ENABLE_COLOR', 'true').lower() == 'true'
    LOG_ROTATION_WHEN = os.getenv('LOG_ROTATION_WHEN', 'midnight')  # midnight, hour, day
    LOG_ROTATION_INTERVAL = int(os.getenv('LOG_ROTATION_INTERVAL', 1))
    LOG_COMPRESS_OLD = os.getenv('LOG_COMPRESS_OLD', 'true').lower() == 'true'

    # 界面配置
    APP_NAME = os.getenv('APP_NAME', "文件管理系统")
    THEME_COLOR = os.getenv('THEME_COLOR', "#4a6fa5")
    SECONDARY_COLOR = os.getenv('SECONDARY_COLOR', "#6c8ebf")

    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    ENABLE_DOWNLOAD = os.getenv('ENABLE_DOWNLOAD', 'true').lower() == 'true'
    ENABLE_DELETE = os.getenv('ENABLE_DELETE', 'true').lower() == 'true'
    ENABLE_UPLOAD = os.getenv('ENABLE_UPLOAD', 'true').lower() == 'true'
    ENABLE_CREATE_FOLDER = os.getenv('ENABLE_CREATE_FOLDER', 'true').lower() == 'true'
    ENABLE_RENAME = os.getenv('ENABLE_RENAME', 'true').lower() == 'true'
    ENABLE_MOVE_COPY = os.getenv('ENABLE_MOVE_COPY', 'true').lower() == 'true'
    ENABLE_FILE_OPS = os.getenv('ENABLE_FILE_OPS', 'true').lower() == 'true'

    # 安全限制
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))  # 100MB单文件限制
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per minute')  # 速率限制
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 会话超时时间(秒)

    # Flask服务器配置
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 8888))
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD', 'false').lower() == 'true'

    # 静态文件配置
    STATIC_VERSION = os.getenv('STATIC_VERSION', '1.0.0')
    SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv('SEND_FILE_MAX_AGE_DEFAULT', 3600))
    STATIC_COMPRESS = os.getenv('STATIC_COMPRESS', 'true').lower() == 'true'

    # 前端资源配置
    FRONTEND_CONFIG = {
        'app_name': os.getenv('APP_NAME', '文件管理系统'),
        'default_view': os.getenv('DEFAULT_VIEW', 'list'),
        'page_size': int(os.getenv('PAGE_SIZE', 20)),
        'show_hidden': os.getenv('SHOW_HIDDEN', 'false').lower() == 'true',
        'enable_drag_drop': os.getenv('ENABLE_DRAG_DROP', 'true').lower() == 'true',
        'enable_preview': os.getenv('ENABLE_PREVIEW', 'true').lower() == 'true'
    }

    # 细粒度权限控制
    PERMISSIONS = {
        'upload': os.getenv('PERMISSION_UPLOAD', 'true').lower() == 'true',
        'download': os.getenv('PERMISSION_DOWNLOAD', 'true').lower() == 'true',
        'delete': os.getenv('PERMISSION_DELETE', 'true').lower() == 'true',
        'rename': os.getenv('PERMISSION_RENAME', 'true').lower() == 'true',
        'create_folder': os.getenv('PERMISSION_CREATE_FOLDER', 'true').lower() == 'true',
        'admin_ops': os.getenv('PERMISSION_ADMIN_OPS', 'false').lower() == 'true'
    }

    # 开发/生产环境配置
    ENV = os.getenv('ENV', 'production')
    
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
        
        # 动态配置文件类型限制
        self._setup_file_extensions()
    
    def _setup_log_file_path(self):
        """确保日志文件路径是绝对路径"""
        if not os.path.isabs(self.LOG_FILE):
            # 如果是相对路径，则相对于项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.LOG_FILE = os.path.normpath(os.path.join(project_root, self.LOG_FILE))
    
    def _setup_file_extensions(self):
        """动态设置文件扩展名限制"""
        # 从环境变量读取禁止的文件扩展名
        forbidden_env = os.getenv('FORBIDDEN_EXTENSIONS', '')
        if forbidden_env:
            forbidden_list = [ext.strip() for ext in forbidden_env.split(',') if ext.strip()]
            self.FORBIDDEN_EXTENSIONS = set(forbidden_list)
        
        # 从环境变量读取允许的文件扩展名
        allowed_env = os.getenv('ALLOWED_EXTENSIONS', '')
        if allowed_env:
            allowed_list = [ext.strip() for ext in allowed_env.split(',') if ext.strip()]
            self.ALLOWED_EXTENSIONS = set(allowed_list)
        
        # 根据ALLOW_EXECUTABLE_FILES设置调整禁止列表
        if not self.ALLOW_EXECUTABLE_FILES:
            # 如果不允许可执行文件，添加常见的可执行文件扩展名
            executable_exts = {'.exe', '.msi', '.app', '.dmg', '.deb', '.rpm'}
            self.FORBIDDEN_EXTENSIONS.update(executable_exts)
        else:
            # 如果允许可执行文件，从禁止列表中移除.exe
            self.FORBIDDEN_EXTENSIONS.discard('.exe')
            self.FORBIDDEN_EXTENSIONS.discard('.msi')
            self.FORBIDDEN_EXTENSIONS.discard('.app')
