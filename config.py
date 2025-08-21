import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 应用配置
class Config:
    # 根目录配置（使用当前目录）
    ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
    
    # 如果环境变量设置的是无效路径，则使用当前目录
    if ROOT_DIR == '/path/to/your/files' or not os.path.exists(ROOT_DIR):
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 上传文件大小限制（单位：字节，默认50GB）
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024 * 1024))

    # 允许上传的文件类型（设置为空集合表示允许所有类型）
    ALLOWED_EXTENSIONS = set()

    # 禁止的文件扩展名
    FORBIDDEN_EXTENSIONS = {}

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 可选：DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', 'file_manager.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    # 界面配置
    APP_NAME = os.getenv('APP_NAME', "文件管理系统")
    THEME_COLOR = os.getenv('THEME_COLOR', "#4a6fa5")  # 主题颜色
    SECONDARY_COLOR = os.getenv('SECONDARY_COLOR', "#6c8ebf")  # 次要颜色

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
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')  # 监听地址
    SERVER_PORT = int(os.getenv('SERVER_PORT', 8888))  # 监听端口
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'  # 调试模式开关
    TEMPLATES_AUTO_RELOAD = os.getenv('TEMPLATES_AUTO_RELOAD', 'false').lower() == 'true'  # 模板自动重载

    # 静态文件配置
    STATIC_VERSION = os.getenv('STATIC_VERSION', '1.0.0')  # 静态资源版本号
    SEND_FILE_MAX_AGE_DEFAULT = int(os.getenv('SEND_FILE_MAX_AGE_DEFAULT', 3600))  # 静态文件缓存时间(秒)
    STATIC_COMPRESS = os.getenv('STATIC_COMPRESS', 'true').lower() == 'true'  # 是否启用静态资源压缩

    # 前端资源配置
    FRONTEND_CONFIG = {
        'app_name': os.getenv('APP_NAME', '文件管理系统'),
        'default_view': os.getenv('DEFAULT_VIEW', 'list'),  # 默认视图(list/grid)
        'page_size': int(os.getenv('PAGE_SIZE', 20)),  # 每页显示文件数
        'show_hidden': os.getenv('SHOW_HIDDEN', 'false').lower() == 'true',  # 是否显示隐藏文件
        'enable_drag_drop': os.getenv('ENABLE_DRAG_DROP', 'true').lower() == 'true',  # 启用拖拽上传
        'enable_preview': os.getenv('ENABLE_PREVIEW', 'true').lower() == 'true'  # 启用文件预览
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
    ENV = os.getenv('ENV', 'production')  # 当前环境(development/production)
    
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
