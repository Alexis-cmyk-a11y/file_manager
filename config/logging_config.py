"""
日志配置文件
提供不同环境的日志配置选项
"""

import os
from pathlib import Path

# 基础日志配置
BASE_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'json': {
            '()': 'utils.logger.JSONFormatter'
        },
        'colored': {
            '()': 'utils.logger.ColoredFormatter',
            'format': '%(timestamp)s - %(levelname)s - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': 'logs/file_manager.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8'
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'filename': 'logs/error.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8'
        },
        'access_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/access.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {  # 根日志记录器
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'file_manager': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'file_manager.app': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        },
        'file_manager.services': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'file_manager.api': {
            'handlers': ['file', 'access_file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        },
        'werkzeug': {  # Flask开发服务器
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# 开发环境配置
DEVELOPMENT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'colored': {
            '()': 'utils.logger.ColoredFormatter',
            'format': '%(timestamp)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s'
        },
        'json': {
            '()': 'utils.logger.JSONFormatter'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': 'logs/dev.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# 生产环境配置
PRODUCTION_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'utils.logger.JSONFormatter'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filename': 'logs/production.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 90,
            'encoding': 'utf-8'
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'json',
            'filename': 'logs/error.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 90,
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        '': {
            'handlers': ['file', 'error_file'],
            'level': 'WARNING',
            'propagate': False
        },
        'file_manager': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# 测试环境配置
TEST_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'WARNING',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False
        }
    }
}

def get_logging_config(environment='development'):
    """根据环境获取日志配置"""
    configs = {
        'development': DEVELOPMENT_LOGGING_CONFIG,
        'production': PRODUCTION_LOGGING_CONFIG,
        'test': TEST_LOGGING_CONFIG
    }
    
    return configs.get(environment, BASE_LOGGING_CONFIG)

def setup_log_directories():
    """创建日志目录"""
    log_dirs = ['logs', 'logs/archive', 'logs/backup']
    
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

def get_log_file_path(filename, environment='development'):
    """获取日志文件路径"""
    base_dir = 'logs'
    
    if environment == 'production':
        base_dir = 'logs/production'
    elif environment == 'test':
        base_dir = 'logs/test'
    
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    return os.path.join(base_dir, filename)
