import os

# 应用配置
class Config:
    # 根目录配置（使用当前目录）
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 上传文件大小限制（单位：MB）
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024 * 1024

    # 允许上传的文件类型（为空表示允许所有类型）
    ALLOWED_EXTENSIONS = set()

    # 日志配置
    LOG_LEVEL = 'INFO'  # 可选：DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'file_manager.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    # 界面配置
    APP_NAME = "文件管理系统"
    THEME_COLOR = "#4a6fa5"  # 主题颜色
    SECONDARY_COLOR = "#6c8ebf"  # 次要颜色

    # 安全配置
    ENABLE_DOWNLOAD = True  # 是否允许下载文件
    ENABLE_DELETE = True    # 是否允许删除文件/文件夹
    ENABLE_UPLOAD = True    # 是否允许上传文件
    ENABLE_CREATE_FOLDER = True  # 是否允许创建文件夹
    ENABLE_RENAME = True    # 是否允许重命名
    ENABLE_MOVE_COPY = True  # 是否允许移动/复制
    ENABLE_FILE_OPS = True  # 控制复制、移动和删除操作

    # Flask服务器配置
    SERVER_HOST = '0.0.0.0'  # 监听地址
    SERVER_PORT = 8888       # 监听端口
    DEBUG_MODE = True        # 调试模式开关
    TEMPLATES_AUTO_RELOAD = True  # 模板自动重载

    # 静态文件配置
    STATIC_VERSION = '1.0.0'  # 静态资源版本号
    SEND_FILE_MAX_AGE_DEFAULT = 3600  # 静态文件缓存时间(秒)
    STATIC_COMPRESS = True    # 是否启用静态资源压缩

    # 前端资源配置
    FRONTEND_CONFIG = {
        'app_name': '文件管理系统',
        'default_view': 'list',  # 默认视图(list/grid)
        'page_size': 20,         # 每页显示文件数
        'show_hidden': False     # 是否显示隐藏文件
    }

    # 细粒度权限控制
    PERMISSIONS = {
        'upload': True,      # 上传权限
        'download': True,    # 下载权限
        'delete': True,      # 删除权限
        'rename': True,      # 重命名权限
        'create_folder': True, # 创建文件夹权限
        'admin_ops': False   # 管理员操作权限
    }

    # 开发/生产环境配置
    ENV = 'development'  # 当前环境(development/production)
    if ENV == 'production':
        DEBUG_MODE = False
        TEMPLATES_AUTO_RELOAD = False
        STATIC_COMPRESS = True
