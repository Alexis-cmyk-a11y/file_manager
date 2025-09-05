"""
缓存服务模块
提供Redis和内存缓存的双重保障
"""

import os
import time
import hashlib
import json
from typing import Any, Optional, Union
from utils.logger import get_logger

logger = get_logger(__name__)

class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.memory_cache = {}
        self.redis_service = None
        self._init_redis()
    
    def _init_redis(self):
        """初始化Redis服务"""
        try:
            from services.redis_service import get_redis_service
            self.redis_service = get_redis_service()
            if self.redis_service and self.redis_service.is_connected():
                logger.info("Redis缓存服务已启用")
            else:
                logger.warning("Redis服务不可用，将使用内存缓存")
                self.redis_service = None
        except Exception as e:
            logger.warning(f"Redis服务初始化失败: {e}")
            self.redis_service = None
    
    def _get_cache_ttl(self, key: str, data_type: str = None, data_size: int = None) -> int:
        """根据缓存键类型和数据特征动态调整TTL"""
        # 目录列表缓存策略
        if key.startswith('dir_listing:'):
            if key == 'dir_listing:':  # 根目录
                return 300  # 5分钟
            elif data_size and data_size > 1000:  # 大目录
                return 60   # 1分钟
            else:
                return 180  # 3分钟
        
        # 文件信息缓存策略
        elif key.startswith('file_info:'):
            return 600  # 10分钟
        
        # 用户会话缓存
        elif key.startswith('session:'):
            return 3600  # 1小时
        
        # 系统配置缓存
        elif key.startswith('config:'):
            return 1800  # 30分钟
        
        # 默认缓存时间
        return 300
    
    def _generate_cache_key(self, prefix: str, *args) -> str:
        """生成缓存键"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ':'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()[:16]
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            # 1. 先检查内存缓存
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if time.time() < item['expires_at']:
                    logger.debug(f"从内存缓存获取: {key}")
                    return item['value']
                else:
                    # 清理过期缓存
                    del self.memory_cache[key]
            
            # 2. 检查Redis缓存
            if self.redis_service and self.redis_service.is_connected():
                try:
                    value = self.redis_service.get(key)
                    if value:
                        logger.debug(f"从Redis缓存获取: {key}")
                        return value
                except Exception as e:
                    logger.warning(f"Redis获取缓存失败: {e}")
            
            return default
            
        except Exception as e:
            logger.error(f"获取缓存失败: {key}, 错误: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            data_type: str = None, data_size: int = None) -> bool:
        """设置缓存值"""
        try:
            # 动态计算TTL
            if ttl is None:
                ttl = self._get_cache_ttl(key, data_type, data_size)
            
            # 1. 设置内存缓存
            expires_at = time.time() + ttl
            self.memory_cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            
            # 2. 设置Redis缓存
            if self.redis_service and self.redis_service.is_connected():
                try:
                    # 序列化数据
                    if isinstance(value, (dict, list)):
                        serialized_value = json.dumps(value, ensure_ascii=False)
                    else:
                        serialized_value = str(value)
                    
                    self.redis_service.set(key, serialized_value, ex=ttl)
                    logger.debug(f"缓存已设置: {key}, TTL: {ttl}s")
                except Exception as e:
                    logger.warning(f"Redis设置缓存失败: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {key}, 错误: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            # 删除内存缓存
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 删除Redis缓存
            if self.redis_service and self.redis_service.is_connected():
                try:
                    self.redis_service.delete(key)
                except Exception as e:
                    logger.warning(f"Redis删除缓存失败: {e}")
            
            logger.debug(f"缓存已删除: {key}")
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {key}, 错误: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存"""
        cleared_count = 0
        
        try:
            import re
            
            # 将通配符模式转换为正则表达式
            if '*' in pattern:
                # 将 * 转换为 .* 进行正则匹配
                regex_pattern = pattern.replace('*', '.*')
                regex = re.compile(regex_pattern)
            else:
                # 如果没有通配符，使用简单的字符串包含匹配
                regex = None
            
            # 清除内存缓存
            if regex:
                keys_to_delete = [k for k in self.memory_cache.keys() if regex.match(k)]
            else:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                cleared_count += 1
            
            # 清除Redis缓存
            if self.redis_service and self.redis_service.is_connected():
                try:
                    # 获取匹配的键
                    keys = self.redis_service.keys(pattern)
                    if keys:
                        self.redis_service.delete(*keys)
                        cleared_count += len(keys)
                except Exception as e:
                    logger.warning(f"Redis清除模式缓存失败: {e}")
            
            logger.info(f"清除模式缓存完成: {pattern}, 共清除 {cleared_count} 个")
            return cleared_count
            
        except Exception as e:
            logger.error(f"清除模式缓存失败: {pattern}, 错误: {e}")
            return cleared_count
    
    def get_stats(self) -> dict:
        """获取缓存统计信息"""
        try:
            stats = {
                'memory_cache': {
                    'total_keys': len(self.memory_cache),
                    'memory_usage': len(str(self.memory_cache)),
                    'expired_keys': 0
                },
                'redis_cache': {
                    'connected': False,
                    'total_keys': 0,
                    'memory_usage': 0
                }
            }
            
            # 统计过期键
            current_time = time.time()
            expired_keys = [k for k, v in self.memory_cache.items() 
                          if current_time >= v['expires_at']]
            stats['memory_cache']['expired_keys'] = len(expired_keys)
            
            # Redis统计
            if self.redis_service and self.redis_service.is_connected():
                try:
                    stats['redis_cache']['connected'] = True
                    # 这里可以添加更多Redis统计信息
                except Exception:
                    pass
            
            return stats
            
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        try:
            current_time = time.time()
            expired_keys = [k for k, v in self.memory_cache.items() 
                          if current_time >= v['expires_at']]
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            logger.info(f"清理过期缓存完成，共清理 {len(expired_keys)} 个")
            return len(expired_keys)
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def _get_redis_service(self):
        """获取Redis服务实例"""
        return self.redis_service

# 全局缓存服务实例
_cache_service = None

def get_cache_service() -> CacheService:
    """获取缓存服务实例"""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service

def clear_cache_service():
    """清理缓存服务实例"""
    global _cache_service
    if _cache_service:
        _cache_service = None
