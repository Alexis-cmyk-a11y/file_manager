"""
Redis服务模块
提供Redis连接管理和常用操作
"""

import redis
import json
import pickle
from typing import Any, Optional, Union, List, Dict
from utils.logger import get_logger

logger = get_logger('redis_service')

class RedisService:
    """Redis服务类"""
    
    def __init__(self, config=None):
        """初始化Redis服务"""
        if config is None:
            # 延迟导入避免循环依赖
            from core.config import Config
            config = Config()
        
        self.config = config
        self._redis_client = None
        self._connection_pool = None
        self._init_connection()
    
    def _init_connection(self):
        """初始化Redis连接"""
        try:
            logger.info(f"正在初始化Redis连接: {self.config.REDIS_HOST}:{self.config.REDIS_PORT}")
            
            # 创建连接池（移除不支持的ssl相关参数）
            pool_kwargs = {
                'host': self.config.REDIS_HOST,
                'port': self.config.REDIS_PORT,
                'db': self.config.REDIS_DB,
                'password': self.config.REDIS_PASSWORD,
                'max_connections': self.config.REDIS_CONNECTION_POOL_SIZE,
                'socket_timeout': self.config.REDIS_SOCKET_TIMEOUT,
                'socket_connect_timeout': self.config.REDIS_SOCKET_CONNECT_TIMEOUT,
                'retry_on_timeout': self.config.REDIS_RETRY_ON_TIMEOUT,
                'health_check_interval': self.config.REDIS_HEALTH_CHECK_INTERVAL,
                'decode_responses': True  # 自动解码响应
            }
            
            # 只有在启用SSL时才添加SSL相关参数
            if self.config.REDIS_SSL:
                pool_kwargs['ssl'] = self.config.REDIS_SSL
                pool_kwargs['ssl_cert_reqs'] = self.config.REDIS_SSL_CERT_REQS
            
            self._connection_pool = redis.ConnectionPool(**pool_kwargs)
            
            # 创建Redis客户端
            self._redis_client = redis.Redis(connection_pool=self._connection_pool)
            logger.info(f"Redis客户端创建成功: {self._redis_client}")
            
            # 测试连接
            ping_result = self._redis_client.ping()
            logger.info(f"Redis PING测试结果: {ping_result}")
            logger.info(f"Redis连接成功: {self.config.REDIS_HOST}:{self.config.REDIS_PORT}")
            
        except redis.ConnectionError as e:
            logger.error(f"Redis连接失败: {e}")
            self._redis_client = None
        except Exception as e:
            logger.error(f"Redis初始化错误: {e}")
            self._redis_client = None
    
    def is_connected(self) -> bool:
        """检查Redis是否已连接"""
        if self._redis_client is None:
            return False
        
        try:
            self._redis_client.ping()
            return True
        except:
            return False
    
    def reconnect(self):
        """重新连接Redis"""
        logger.info("尝试重新连接Redis...")
        self._init_connection()
    
    def get_client(self) -> Optional[redis.Redis]:
        """获取Redis客户端实例"""
        if not self.is_connected():
            self.reconnect()
        return self._redis_client
    
    # 字符串操作
    def set(self, key: str, value: Any, ex: Optional[int] = None, nx: bool = False, xx: bool = False) -> bool:
        """设置键值对"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return client.set(key, value, ex=ex, nx=nx, xx=xx)
        except Exception as e:
            logger.error(f"Redis SET操作失败: {e}")
            return False
    
    def setex(self, key: str, time: int, value: Any) -> bool:
        """设置键值对并指定过期时间"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return client.setex(key, time, value)
        except Exception as e:
            logger.error(f"Redis SETEX操作失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取键值"""
        try:
            client = self.get_client()
            if client is None:
                return default
            
            value = client.get(key)
            if value is None:
                return default
            
            # 对于验证码等简单字符串，直接返回
            # 只有在明确知道是JSON格式时才尝试解析
            if key.startswith('verification:') or key.startswith('cooldown:'):
                return value
            
            # 尝试解析JSON（用于其他复杂数据）
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logger.error(f"Redis GET操作失败: {e}")
            return default
    
    def delete(self, *keys: str) -> int:
        """删除键"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            return client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE操作失败: {e}")
            return 0
    
    def exists(self, *keys: str) -> int:
        """检查键是否存在"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            return client.exists(*keys)
        except Exception as e:
            logger.error(f"Redis EXISTS操作失败: {e}")
            return 0
    
    def expire(self, key: str, time: int) -> bool:
        """设置键过期时间"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            return client.expire(key, time)
        except Exception as e:
            logger.error(f"Redis EXPIRE操作失败: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        try:
            client = self.get_client()
            if client is None:
                return -2
            
            return client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL操作失败: {e}")
            return -2
    
    def incr(self, key: str, amount: int = 1) -> int:
        """增加键的值"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            return client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR操作失败: {e}")
            return 0
    
    # 哈希操作
    def hset(self, name: str, key: str, value: Any) -> int:
        """设置哈希字段"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            
            return client.hset(name, key, value)
        except Exception as e:
            logger.error(f"Redis HSET操作失败: {e}")
            return 0
    
    def hget(self, name: str, key: str, default: Any = None) -> Any:
        """获取哈希字段"""
        try:
            client = self.get_client()
            if client is None:
                return default
            
            value = client.hget(name, key)
            if value is None:
                return default
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logger.error(f"Redis HGET操作失败: {e}")
            return default
    
    def hgetall(self, name: str) -> Dict[str, Any]:
        """获取哈希所有字段"""
        try:
            client = self.get_client()
            if client is None:
                return {}
            
            result = client.hgetall(name)
            if not result:
                return {}
            
            # 尝试解析JSON值
            parsed_result = {}
            for k, v in result.items():
                try:
                    parsed_result[k] = json.loads(v)
                except:
                    parsed_result[k] = v
            
            return parsed_result
        except Exception as e:
            logger.error(f"Redis HGETALL操作失败: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            return client.hdel(name, *keys)
        except Exception as e:
            logger.error(f"Redis HDEL操作失败: {e}")
            return 0
    
    # 列表操作
    def lpush(self, name: str, *values: Any) -> int:
        """从左侧推入列表"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return client.lpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis LPUSH操作失败: {e}")
            return 0
    
    def rpush(self, name: str, *values: Any) -> int:
        """从右侧推入列表"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return client.rpush(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis RPUSH操作失败: {e}")
            return 0
    
    def lpop(self, name: str, default: Any = None) -> Any:
        """从左侧弹出列表元素"""
        try:
            client = self.get_client()
            if client is None:
                return default
            
            value = client.lpop(name)
            if value is None:
                return default
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logger.error(f"Redis LPOP操作失败: {e}")
            return default
    
    def rpop(self, name: str, default: Any = None) -> Any:
        """从右侧弹出列表元素"""
        try:
            client = self.get_client()
            if client is None:
                return default
            
            value = client.rpop(name)
            if value is None:
                return default
            
            # 尝试解析JSON
            try:
                return json.loads(value)
            except:
                return value
        except Exception as e:
            logger.error(f"Redis RPOP操作失败: {e}")
            return default
    
    def lrange(self, name: str, start: int, end: int) -> List[Any]:
        """获取列表范围"""
        try:
            client = self.get_client()
            if client is None:
                return []
            
            result = client.lrange(name, start, end)
            if not result:
                return []
            
            # 尝试解析JSON值
            parsed_result = []
            for value in result:
                try:
                    parsed_result.append(json.loads(value))
                except:
                    parsed_result.append(value)
            
            return parsed_result
        except Exception as e:
            logger.error(f"Redis LRANGE操作失败: {e}")
            return []
    
    # 集合操作
    def sadd(self, name: str, *values: Any) -> int:
        """添加集合元素"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return client.sadd(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis SADD操作失败: {e}")
            return 0
    
    def srem(self, name: str, *values: Any) -> int:
        """删除集合元素"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            # 序列化值
            serialized_values = []
            for value in values:
                if isinstance(value, (dict, list)):
                    serialized_values.append(json.dumps(value, ensure_ascii=False))
                else:
                    serialized_values.append(str(value))
            
            return client.srem(name, *serialized_values)
        except Exception as e:
            logger.error(f"Redis SREM操作失败: {e}")
            return 0
    
    def smembers(self, name: str) -> set:
        """获取集合所有元素"""
        try:
            client = self.get_client()
            if client is None:
                return set()
            
            result = client.smembers(name)
            if not result:
                return set()
            
            # 尝试解析JSON值
            parsed_result = set()
            for value in result:
                try:
                    parsed_result.add(json.loads(value))
                except:
                    parsed_result.add(value)
            
            return parsed_result
        except Exception as e:
            logger.error(f"Redis SMEMBERS操作失败: {e}")
            return set()
    
    # 有序集合操作
    def zadd(self, name: str, mapping: Dict[str, float]) -> int:
        """添加有序集合元素"""
        try:
            client = self.get_client()
            if client is None:
                return 0
            
            # 序列化键
            serialized_mapping = {}
            for key, score in mapping.items():
                if isinstance(key, (dict, list)):
                    serialized_key = json.dumps(key, ensure_ascii=False)
                else:
                    serialized_key = str(key)
                serialized_mapping[serialized_key] = score
            
            return client.zadd(name, serialized_mapping)
        except Exception as e:
            logger.error(f"Redis ZADD操作失败: {e}")
            return 0
    
    def zrange(self, name: str, start: int, end: int, desc: bool = False, withscores: bool = False) -> List[Any]:
        """获取有序集合范围"""
        try:
            client = self.get_client()
            if client is None:
                return []
            
            result = client.zrange(name, start, end, desc=desc, withscores=withscores)
            if not result:
                return []
            
            if withscores:
                # 返回带分数的结果
                parsed_result = []
                for i in range(0, len(result), 2):
                    if i + 1 < len(result):
                        key, score = result[i], result[i + 1]
                        try:
                            parsed_result.append((json.loads(key), score))
                        except:
                            parsed_result.append((key, score))
                return parsed_result
            else:
                # 返回不带分数的结果
                parsed_result = []
                for value in result:
                    try:
                        parsed_result.append(json.loads(value))
                    except:
                        parsed_result.append(value)
                return parsed_result
        except Exception as e:
            logger.error(f"Redis ZRANGE操作失败: {e}")
            return []
    
    # 通用操作
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键"""
        try:
            client = self.get_client()
            if client is None:
                return []
            
            return client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS操作失败: {e}")
            return []
    
    def flushdb(self) -> bool:
        """清空当前数据库"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB操作失败: {e}")
            return False
    
    def info(self, section: Optional[str] = None) -> Dict[str, Any]:
        """获取Redis信息"""
        try:
            client = self.get_client()
            if client is None:
                return {}
            
            return client.info(section)
        except Exception as e:
            logger.error(f"Redis INFO操作失败: {e}")
            return {}
    
    def ping(self) -> bool:
        """测试Redis连接"""
        try:
            client = self.get_client()
            if client is None:
                return False
            
            return client.ping()
        except Exception as e:
            logger.error(f"Redis PING操作失败: {e}")
            return False
    
    def close(self):
        """关闭Redis连接"""
        try:
            if self._redis_client:
                self._redis_client.close()
            if self._connection_pool:
                self._connection_pool.disconnect()
            logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接时出错: {e}")

# 全局Redis服务实例
_redis_service = None

def get_redis_service() -> RedisService:
    """获取全局Redis服务实例"""
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service

def close_redis_service():
    """关闭全局Redis服务实例"""
    global _redis_service
    if _redis_service:
        _redis_service.close()
        _redis_service = None
