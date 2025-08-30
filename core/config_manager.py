"""
配置管理模块
支持多环境配置、热重载、配置验证等功能
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import hashlib
import secrets

@dataclass
class AppConfig:
    """应用配置数据类"""
    name: str = "文件管理系统"
    version: str = "2.0.0"
    description: str = "现代化的文件管理系统"
    author: str = "File Manager Team"
    contact: str = "support@filemanager.local"

@dataclass
class ServerConfig:
    """服务器配置数据类"""
    host: str = "127.0.0.1"
    port: int = 8888
    workers: int = 1
    timeout: int = 30
    debug: bool = False

@dataclass
class DatabaseConfig:
    """数据库配置数据类"""
    mysql: Dict[str, Any] = field(default_factory=dict)
    redis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    """安全配置数据类"""
    secret_key: Optional[str] = None
    session_timeout: int = 3600
    rate_limit: str = "100 per minute"
    jwt_expiration: int = 86400
    password_policy: Dict[str, Any] = field(default_factory=dict)
    file_validation: Dict[str, Any] = field(default_factory=dict)
    cors: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoggingConfig:
    """日志配置数据类"""
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/file_manager.log"
    max_size: int = 10485760
    backup_count: int = 30
    console: Dict[str, Any] = field(default_factory=dict)
    file_config: Dict[str, Any] = field(default_factory=dict)
    json: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheConfig:
    """缓存配置数据类"""
    enabled: bool = True
    default_ttl: int = 300
    max_items: int = 10000
    strategies: Dict[str, int] = field(default_factory=dict)
    redis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FrontendConfig:
    """前端配置数据类"""
    app_name: str = "文件管理系统"
    theme: Dict[str, str] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)
    editor: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)
    upload: Dict[str, Any] = field(default_factory=dict)
    download: Dict[str, Any] = field(default_factory=dict)
    preview: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    i18n: Dict[str, Any] = field(default_factory=dict)
    shortcuts: Dict[str, str] = field(default_factory=dict)
    error_handling: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FilesystemConfig:
    """文件系统配置数据类"""
    root_directory: Optional[str] = None
    upload: Dict[str, Any] = field(default_factory=dict)
    download: Dict[str, Any] = field(default_factory=dict)
    preview: Dict[str, Any] = field(default_factory=dict)
    storage: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceConfig:
    """性能监控配置数据类"""
    monitoring_enabled: bool = True
    slow_threshold: float = 1.0
    metrics_retention: int = 100
    profiling: Dict[str, Any] = field(default_factory=dict)
    alerts: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MonitoringConfig:
    """监控配置数据类"""
    health_check: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config", environment: str = None):
        self.config_dir = Path(config_dir)
        self.environment = environment or self._detect_environment()
        self.config_data = {}
        self.last_modified = None
        self.config_hash = None
        self.logger = logging.getLogger(__name__)
        
        # 初始化配置
        self._load_config()
        self._validate_config()
        
    def _detect_environment(self) -> str:
        """检测运行环境"""
        # 优先从环境文件读取
        env_file = self.config_dir / "environment.txt"
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    env = f.read().strip()
                    if env in ['development', 'production']:
                        return env
            except Exception as e:
                self.logger.warning(f"读取环境文件失败: {e}")
        
        # 从系统环境变量读取（仅作为备选）
        env = os.getenv('FLASK_ENV', 'development')
        if env not in ['development', 'production']:
            env = 'development'
        
        return env
    
    def _load_config(self):
        """加载配置文件"""
        try:
            # 加载主配置文件
            main_config_file = self.config_dir / "config.yaml"
            if main_config_file.exists():
                with open(main_config_file, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
            else:
                self.logger.warning("主配置文件不存在，使用默认配置")
                self.config_data = {}
            
            # 加载环境特定配置
            env_config_file = self.config_dir / f"{self.environment}.yaml"
            if env_config_file.exists():
                with open(env_config_file, 'r', encoding='utf-8') as f:
                    env_config = yaml.safe_load(f)
                    self._merge_config(self.config_data, env_config)
            
            # 更新修改时间和哈希值
            self.last_modified = datetime.now()
            self.config_hash = self._calculate_config_hash()
            
            self.logger.info(f"配置加载完成，环境: {self.environment}")
            
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            raise
    
    def _merge_config(self, base: Dict, override: Dict):
        """递归合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _calculate_config_hash(self) -> str:
        """计算配置哈希值"""
        config_str = json.dumps(self.config_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(config_str.encode('utf-8')).hexdigest()
    
    def _validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 验证必需配置
        required_keys = ['environments', 'database', 'security', 'logging']
        for key in required_keys:
            if key not in self.config_data:
                errors.append(f"缺少必需配置: {key}")
        
        # 验证环境配置
        if 'environments' in self.config_data:
            if self.environment not in self.config_data['environments']:
                errors.append(f"环境配置不存在: {self.environment}")
        
        # 验证数据库配置
        if 'database' in self.config_data:
            db_config = self.config_data['database']
            if 'mysql' not in db_config:
                errors.append("缺少MySQL数据库配置")
            if 'redis' not in db_config:
                errors.append("缺少Redis配置")
        
        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"  - {error}" for error in errors)
            self.logger.error(error_msg)
            raise ValueError(error_msg)
    
    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            old_hash = self.config_hash
            self._load_config()
            self._validate_config()
            
            if old_hash != self.config_hash:
                self.logger.info("配置已更新并重新加载")
                return True
            else:
                self.logger.info("配置无变化")
                return False
                
        except Exception as e:
            self.logger.error(f"重新加载配置失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
        except Exception:
            return default
    
    def get_environment_config(self) -> Dict[str, Any]:
        """获取当前环境的配置"""
        return self.config_data.get('environments', {}).get(self.environment, {})
    
    def get_server_config(self) -> ServerConfig:
        """获取服务器配置"""
        env_config = self.get_environment_config()
        server_config = env_config.get('server', {})
        
        return ServerConfig(
            host=server_config.get('host', '127.0.0.1'),
            port=server_config.get('port', 8888),
            workers=server_config.get('workers', 1),
            timeout=server_config.get('timeout', 30),
            debug=env_config.get('debug', False)
        )
    
    def get_database_config(self) -> DatabaseConfig:
        """获取数据库配置"""
        db_config = self.config_data.get('database', {})
        
        return DatabaseConfig(
            mysql=db_config.get('mysql', {}),
            redis=db_config.get('redis', {})
        )
    
    def get_security_config(self) -> SecurityConfig:
        """获取安全配置"""
        security_config = self.config_data.get('security', {})
        
        # 自动生成密钥
        if not security_config.get('secret_key'):
            security_config['secret_key'] = secrets.token_hex(32)
        
        return SecurityConfig(
            secret_key=security_config.get('secret_key'),
            session_timeout=security_config.get('session_timeout', 3600),
            rate_limit=security_config.get('rate_limit', '100 per minute'),
            jwt_expiration=security_config.get('jwt_expiration', 86400),
            password_policy=security_config.get('password_policy', {}),
            file_validation=security_config.get('file_validation', {}),
            cors=security_config.get('cors', {})
        )
    
    def get_logging_config(self) -> LoggingConfig:
        """获取日志配置"""
        env_config = self.get_environment_config()
        logging_config = self.config_data.get('logging', {})
        
        return LoggingConfig(
            level=env_config.get('log_level', logging_config.get('level', 'INFO')),
            format=logging_config.get('format', 'json'),
            file=logging_config.get('file', 'logs/file_manager.log'),
            max_size=logging_config.get('max_size', 10485760),
            backup_count=logging_config.get('backup_count', 30),
            console=logging_config.get('console', {}),
            file_config=logging_config.get('file_config', {}),
            json=logging_config.get('json', {}),
            performance=logging_config.get('performance', {})
        )
    
    def get_cache_config(self) -> CacheConfig:
        """获取缓存配置"""
        cache_config = self.config_data.get('cache', {})
        
        return CacheConfig(
            enabled=cache_config.get('enabled', True),
            default_ttl=cache_config.get('default_ttl', 300),
            max_items=cache_config.get('max_items', 10000),
            strategies=cache_config.get('strategies', {}),
            redis=cache_config.get('redis', {})
        )
    
    def get_frontend_config(self) -> FrontendConfig:
        """获取前端配置"""
        frontend_config = self.config_data.get('frontend', {})
        
        return FrontendConfig(
            app_name=frontend_config.get('app_name', '文件管理系统'),
            theme=frontend_config.get('theme', {}),
            features=frontend_config.get('features', {}),
            editor=frontend_config.get('editor', {}),
            notifications=frontend_config.get('notifications', {}),
            upload=frontend_config.get('upload', {}),
            download=frontend_config.get('download', {}),
            preview=frontend_config.get('preview', {}),
            performance=frontend_config.get('performance', {}),
            security=frontend_config.get('security', {}),
            i18n=frontend_config.get('i18n', {}),
            shortcuts=frontend_config.get('shortcuts', {}),
            error_handling=frontend_config.get('error_handling', {})
        )
    
    def get_filesystem_config(self) -> FilesystemConfig:
        """获取文件系统配置"""
        filesystem_config = self.config_data.get('filesystem', {})
        
        return FilesystemConfig(
            root_directory=filesystem_config.get('root_directory'),
            upload=filesystem_config.get('upload', {}),
            download=filesystem_config.get('download', {}),
            preview=filesystem_config.get('preview', {}),
            storage=filesystem_config.get('storage', {})
        )
    
    def get_performance_config(self) -> PerformanceConfig:
        """获取性能配置"""
        performance_config = self.config_data.get('performance', {})
        
        return PerformanceConfig(
            monitoring_enabled=performance_config.get('monitoring_enabled', True),
            slow_threshold=performance_config.get('slow_threshold', 1.0),
            metrics_retention=performance_config.get('metrics_retention', 100),
            profiling=performance_config.get('profiling', {}),
            alerts=performance_config.get('alerts', {}),
            metrics=performance_config.get('metrics', {})
        )
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """获取监控配置"""
        monitoring_config = self.config_data.get('monitoring', {})
        
        return MonitoringConfig(
            health_check=monitoring_config.get('health_check', {}),
            metrics=monitoring_config.get('metrics', {}),
            alerts=monitoring_config.get('alerts', {})
        )
    
    def get_feature_flag(self, feature: str) -> bool:
        """获取功能开关状态"""
        env_config = self.get_environment_config()
        features = env_config.get('features', {})
        return features.get(f'enable_{feature}', False)
    
    def get_limit(self, limit_type: str) -> Any:
        """获取限制配置"""
        env_config = self.get_environment_config()
        limits = env_config.get('limits', {})
        return limits.get(limit_type)
    
    def print_config_summary(self):
        """打印配置摘要"""
        print(f"📋 配置摘要:")
        print(f"   🌍 运行环境: {self.environment}")
        print(f"   📁 配置目录: {self.config_dir}")
        print(f"   🔧 调试模式: {self.get_feature_flag('debug')}")
        print(f"   📊 性能监控: {self.get_feature_flag('performance_monitoring')}")
        print(f"   🔒 安全日志: {self.get_feature_flag('security_logging')}")
        print(f"   💾 缓存系统: {self.get_feature_flag('cache')}")
        print(f"   📦 压缩功能: {self.get_feature_flag('compression')}")
        print()
    
    def export_config(self, format: str = 'json') -> str:
        """导出配置"""
        if format == 'json':
            return json.dumps(self.config_data, indent=2, ensure_ascii=False)
        elif format == 'yaml':
            return yaml.dump(self.config_data, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"不支持的导出格式: {format}")
    
    def validate_config_file(self, config_file: str) -> bool:
        """验证配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 基本结构验证
            required_sections = ['environments', 'database', 'security', 'logging']
            for section in required_sections:
                if section not in config:
                    return False
            
            return True
        except Exception:
            return False

# 创建全局配置管理器实例
config_manager = ConfigManager()
