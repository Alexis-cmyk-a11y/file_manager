"""
日志工具模块
提供统一的日志配置、格式化和管理功能
"""

import os
import sys
import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if hasattr(record, 'levelname') and record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # 添加时间戳
        record.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # 添加进程ID
        record.process_id = os.getpid()
        
        # 添加线程ID
        record.thread_id = record.thread if hasattr(record, 'thread') else 'N/A'
        
        return super().format(record)

class JSONFormatter(logging.Formatter):
    """JSON格式日志格式化器"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': getattr(record, 'thread', 'N/A')
        }
        
        # 添加异常信息
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # 添加额外字段
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str, logger: logging.Logger):
        self.name = name
        self.logger = logger
    
    def _log_with_context(self, level: int, message: str, **kwargs):
        """记录带上下文的日志"""
        extra_fields = {
            'context': kwargs.get('context', {}),
            'user_id': kwargs.get('user_id'),
            'request_id': kwargs.get('request_id'),
            'ip_address': kwargs.get('ip_address'),
            'user_agent': kwargs.get('user_agent'),
            'operation': kwargs.get('operation'),
            'file_path': kwargs.get('file_path'),
            'file_size': kwargs.get('file_size'),
            'duration_ms': kwargs.get('duration_ms')
        }
        
        # 过滤掉None值
        extra_fields = {k: v for k, v in extra_fields.items() if v is not None}
        
        record = self.logger.makeRecord(
            self.name, level, '', 0, message, (), None, 
            extra={'extra_fields': extra_fields}
        )
        self.logger.handle(record)
    
    def debug(self, message: str, **kwargs):
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """记录异常日志"""
        kwargs['exception'] = True
        self._log_with_context(logging.ERROR, message, **kwargs)

class LoggerManager:
    """日志管理器"""
    
    def __init__(self, config):
        self.config = config
        self.loggers = {}
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志系统"""
        # 确保日志文件路径是绝对路径
        if not os.path.isabs(self.config.LOG_FILE):
            # 如果是相对路径，则相对于项目根目录
            # 使用更可靠的路径解析方法
            try:
                # 尝试从当前工作目录解析
                project_root = os.getcwd()
                log_file_path = os.path.join(project_root, self.config.LOG_FILE)
            except:
                # 如果失败，使用文件路径解析
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                log_file_path = os.path.join(project_root, self.config.LOG_FILE)
        else:
            log_file_path = self.config.LOG_FILE
        
        log_file_path = Path(log_file_path)
        
        # 创建日志目录
        log_dir = log_file_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置根日志级别
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # 清除根日志记录器的现有处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 为根日志记录器添加文件处理器
        root_file_handler = self._create_file_handler(
            str(log_file_path),
            self.config.LOG_MAX_SIZE,
            self.config.LOG_BACKUP_COUNT
        )
        root_logger.addHandler(root_file_handler)
        
        # 确保根日志记录器不会传播到父级
        root_logger.propagate = False
        
        # 打印调试信息
        print(f"🔍 日志文件路径: {log_file_path}")
        print(f"🔍 日志目录: {log_dir}")
        print(f"🔍 当前工作目录: {Path.cwd()}")
        
        # 配置Flask日志
        self._setup_flask_logging()
        
        # 配置第三方库日志
        self._setup_third_party_logging()
    
    def _setup_flask_logging(self):
        """配置Flask应用日志"""
        app_logger = logging.getLogger('werkzeug')
        app_logger.setLevel(logging.INFO)
        
        # 确保日志文件路径是绝对路径
        if not os.path.isabs(self.config.LOG_FILE):
            # 如果是相对路径，则相对于项目根目录
            # 使用更可靠的路径解析方法
            try:
                # 尝试从当前工作目录解析
                project_root = os.getcwd()
                log_file_path = os.path.join(project_root, self.config.LOG_FILE)
            except:
                # 如果失败，使用文件路径解析
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                log_file_path = os.path.join(project_root, self.config.LOG_FILE)
        else:
            log_file_path = self.config.LOG_FILE
        
        log_file_path = Path(log_file_path)
        
        # 添加文件处理器
        file_handler = self._create_file_handler(
            str(log_file_path),
            self.config.LOG_MAX_SIZE,
            self.config.LOG_BACKUP_COUNT
        )
        app_logger.addHandler(file_handler)
        
        # 添加控制台处理器
        console_handler = self._create_console_handler()
        app_logger.addHandler(console_handler)
    
    def _setup_third_party_logging(self):
        """配置第三方库日志级别"""
        # 设置常见第三方库的日志级别
        third_party_loggers = [
            'urllib3', 'requests', 'boto3', 'botocore',
            'paramiko', 'cryptography', 'PIL', 'matplotlib'
        ]
        
        for logger_name in third_party_loggers:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    def _create_file_handler(self, log_file: str, max_size: int, backup_count: int):
        """创建文件日志处理器"""
        # 确保日志文件路径是绝对路径
        if not os.path.isabs(log_file):
            # 如果是相对路径，则相对于项目根目录
            # 使用更可靠的路径解析方法
            try:
                # 尝试从当前工作目录解析
                project_root = os.getcwd()
                log_file_path = os.path.join(project_root, log_file)
            except:
                # 如果失败，使用文件路径解析
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                log_file_path = os.path.join(project_root, log_file)
        else:
            log_file_path = log_file
        
        log_file_path = Path(log_file_path)
        
        # 确保日志目录存在
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用TimedRotatingFileHandler进行时间轮转
        handler = logging.handlers.TimedRotatingFileHandler(
            str(log_file_path),
            when='midnight',
            interval=1,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # 设置格式化器
        if self.config.LOG_FORMAT == 'json':
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(self.config.LOG_FORMAT)
        
        handler.setFormatter(formatter)
        return handler
    
    def _create_console_handler(self):
        """创建控制台日志处理器"""
        handler = logging.StreamHandler(sys.stdout)
        
        # 根据环境选择格式化器
        if self.config.ENV == 'development':
            formatter = ColoredFormatter(
                '%(timestamp)s - %(levelname)s - %(name)s - %(message)s'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        return handler
    
    def get_logger(self, name: str) -> StructuredLogger:
        """获取结构化日志记录器"""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = StructuredLogger(name, logger)
        
        return self.loggers[name]
    
    def set_level(self, logger_name: str, level: str):
        """设置指定日志记录器的级别"""
        level_num = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger(logger_name).setLevel(level_num)
    
    def add_context_filter(self, logger_name: str, context: Dict[str, Any]):
        """为指定日志记录器添加上下文过滤器"""
        logger = logging.getLogger(logger_name)
        
        class ContextFilter(logging.Filter):
            def filter(self, record):
                record.context = context
                return True
        
        logger.addFilter(ContextFilter())

# 全局日志管理器实例
_logger_manager = None

def get_logger(name: str) -> StructuredLogger:
    """获取日志记录器的便捷函数"""
    global _logger_manager
    if _logger_manager is None:
        from core.config import Config
        _logger_manager = LoggerManager(Config())
    
    return _logger_manager.get_logger(name)

def setup_logging(config):
    """设置日志系统的便捷函数"""
    global _logger_manager
    _logger_manager = LoggerManager(config)
    return _logger_manager

def log_function_call(func):
    """函数调用日志装饰器"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # 记录函数调用
        logger.debug(
            f"调用函数: {func.__name__}",
            operation=f"function_call",
            function_name=func.__name__,
            args_count=len(args),
            kwargs_count=len(kwargs)
        )
        
        try:
            start_time = datetime.now()
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # 记录成功调用
            logger.debug(
                f"函数执行成功: {func.__name__}",
                operation=f"function_success",
                function_name=func.__name__,
                duration_ms=round(duration, 2)
            )
            
            return result
        
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            # 记录异常
            logger.error(
                f"函数执行失败: {func.__name__}",
                operation=f"function_error",
                function_name=func.__name__,
                duration_ms=round(duration, 2),
                error=str(e)
            )
            raise
    
    return wrapper

def log_request_info(func):
    """请求信息日志装饰器"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # 尝试从Flask请求上下文获取信息
        try:
            from flask import request
            if request:
                logger.info(
                    f"处理请求: {func.__name__}",
                    operation="request_handling",
                    method=request.method,
                    url=request.url,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent', 'Unknown')
                )
        except:
            pass
        
        return func(*args, **kwargs)
    
    return wrapper
