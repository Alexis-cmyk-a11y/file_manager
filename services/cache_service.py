"""
缓存服务模块
使用Redis作为后端存储，提供文件管理器的缓存功能
"""

import hashlib
import json
import time
from typing import Any, Optional, Dict, List, Union
from utils.logger import get_logger

logger = get_logger('cache_service')

class CacheService:
    """缓存服务类"""
    
    def __init__(self, default_ttl: int = 3600):
        """初始化缓存服务
        
        Args:
            default_ttl: 默认缓存生存时间（秒）
        """
        self.default_ttl = default_ttl
        # 延迟导入避免循环依赖
        self.redis_service = None
        self.cache_prefix = "file_manager:"
    
    def _get_redis_service(self):
        """获取Redis服务实例（延迟加载）"""
        if self.redis_service is None:
            from services.redis_service import get_redis_service
            self.redis_service = get_redis_service()
        return self.redis_service
    
    def _make_key(self, key: str) -> str:
        """生成缓存键"""
        return f"{self.cache_prefix}{key}"
    
    def _make_hash_key(self, data: Any) -> str:
        """根据数据生成哈希键"""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒），None使用默认值
            
        Returns:
            bool: 是否设置成功
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                logger.warning("Redis未连接，缓存操作失败")
                return False
            
            cache_key = self._make_key(key)
            ttl = ttl if ttl is not None else self.default_ttl
            
            return redis_service.set(cache_key, value, ex=ttl)
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return default
            
            cache_key = self._make_key(key)
            return redis_service.get(cache_key, default)
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return default
    
    def delete(self, key: str) -> bool:
        """删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否删除成功
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return False
            
            cache_key = self._make_key(key)
            return redis_service.delete(cache_key) > 0
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            bool: 是否存在
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return False
            
            cache_key = self._make_key(key)
            return redis_service.exists(cache_key) > 0
        except Exception as e:
            logger.error(f"检查缓存存在性失败: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间
        
        Args:
            key: 缓存键
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否设置成功
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return False
            
            cache_key = self._make_key(key)
            return redis_service.expire(cache_key, ttl)
        except Exception as e:
            logger.error(f"设置缓存过期时间失败: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取缓存剩余生存时间
        
        Args:
            key: 缓存键
            
        Returns:
            int: 剩余生存时间（秒），-1表示永不过期，-2表示键不存在
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return -2
            
            cache_key = self._make_key(key)
            return redis_service.ttl(cache_key)
        except Exception as e:
            logger.error(f"获取缓存生存时间失败: {e}")
            return -2
    
    def clear_pattern(self, pattern: str = "*") -> int:
        """清除匹配模式的缓存
        
        Args:
            pattern: 匹配模式
            
        Returns:
            int: 清除的缓存数量
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return 0
            
            cache_pattern = self._make_key(pattern)
            keys = redis_service.keys(cache_pattern)
            
            if keys:
                return redis_service.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """清除所有缓存
        
        Returns:
            bool: 是否清除成功
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return False
            
            return redis_service.flushdb()
        except Exception as e:
            logger.error(f"清除所有缓存失败: {e}")
            return False
    
    # 文件相关缓存方法
    def cache_file_info(self, file_path: str, file_info: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """缓存文件信息
        
        Args:
            file_path: 文件路径
            file_info: 文件信息
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否缓存成功
        """
        key = f"file_info:{self._make_hash_key(file_path)}"
        return self.set(key, file_info, ttl)
    
    def get_cached_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取缓存的文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息或None
        """
        key = f"file_info:{self._make_hash_key(file_path)}"
        return self.get(key)
    
    def cache_directory_listing(self, dir_path: str, listing: List[Dict[str, Any]], ttl: Optional[int] = None) -> bool:
        """缓存目录列表
        
        Args:
            dir_path: 目录路径
            listing: 目录列表
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否缓存成功
        """
        key = f"dir_listing:{self._make_hash_key(dir_path)}"
        return self.set(key, listing, ttl)
    
    def get_cached_directory_listing(self, dir_path: str) -> Optional[List[Dict[str, Any]]]:
        """获取缓存的目录列表
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录列表或None
        """
        key = f"dir_listing:{self._make_hash_key(dir_path)}"
        return self.get(key)
    
    def invalidate_file_cache(self, file_path: str) -> bool:
        """使文件缓存失效
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否成功
        """
        key = f"file_info:{self._make_hash_key(file_path)}"
        return self.delete(key)
    
    def invalidate_directory_cache(self, dir_path: str) -> bool:
        """使目录缓存失效
        
        Args:
            dir_path: 目录路径
            
        Returns:
            bool: 是否成功
        """
        key = f"dir_listing:{self._make_hash_key(dir_path)}"
        return self.delete(key)
    
    def invalidate_all_file_caches(self) -> int:
        """使所有文件相关缓存失效
        
        Returns:
            int: 清除的缓存数量
        """
        return self.clear_pattern("file_info:*")
    
    def invalidate_all_directory_caches(self) -> int:
        """使所有目录相关缓存失效
        
        Returns:
            int: 清除的缓存数量
        """
        return self.clear_pattern("dir_listing:*")
    
    # 会话和用户相关缓存
    def cache_user_session(self, user_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """缓存用户会话
        
        Args:
            user_id: 用户ID
            session_data: 会话数据
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否缓存成功
        """
        key = f"user_session:{user_id}"
        return self.set(key, session_data, ttl)
    
    def get_user_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            会话数据或None
        """
        key = f"user_session:{user_id}"
        return self.get(key)
    
    def invalidate_user_session(self, user_id: str) -> bool:
        """使用户会话失效
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 是否成功
        """
        key = f"user_session:{user_id}"
        return self.delete(key)
    
    # 统计和监控缓存
    def cache_operation_stats(self, operation: str, stats: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """缓存操作统计
        
        Args:
            operation: 操作名称
            stats: 统计数据
            ttl: 生存时间（秒）
            
        Returns:
            bool: 是否缓存成功
        """
        key = f"stats:{operation}:{int(time.time() // 3600)}"  # 按小时分组
        return self.set(key, stats, ttl)
    
    def get_operation_stats(self, operation: str, hours: int = 24) -> List[Dict[str, Any]]:
        """获取操作统计
        
        Args:
            operation: 操作名称
            hours: 获取多少小时的数据
            
        Returns:
            统计数据列表
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return []
            
            current_hour = int(time.time() // 3600)
            stats = []
            
            for i in range(hours):
                hour = current_hour - i
                key = f"stats:{operation}:{hour}"
                stat = self.get(key)
                if stat:
                    stat['hour'] = hour
                    stats.append(stat)
            
            return stats
        except Exception as e:
            logger.error(f"获取操作统计失败: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        try:
            redis_service = self._get_redis_service()
            if not redis_service or not redis_service.is_connected():
                return {'connected': False}
            
            info = redis_service.info()
            keys = redis_service.keys(f"{self.cache_prefix}*")
            
            return {
                'connected': True,
                'total_keys': len(keys),
                'memory_usage': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {'connected': False, 'error': str(e)}

# 全局缓存服务实例
_cache_service = None

def get_cache_service() -> CacheService:
    """获取全局缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service
