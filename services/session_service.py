"""
用户会话管理服务
提供用户登录状态、偏好设置等会话数据管理
"""

import time
import uuid
from typing import Optional, Dict, Any
from services.cache_service import get_cache_service
from utils.logger import get_logger

logger = get_logger(__name__)

class SessionService:
    """用户会话管理服务类"""
    
    def __init__(self):
        self.cache_service = get_cache_service()
        self.session_prefix = "user_session:"
        self.default_ttl = 3600  # 1小时默认过期时间
    
    def create_session(self, user_id: str, user_data: Dict[str, Any], ttl: Optional[int] = None) -> str:
        """创建用户会话
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            ttl: 会话生存时间（秒）
            
        Returns:
            str: 会话ID
        """
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                'session_id': session_id,
                'user_id': user_id,
                'user_data': user_data,
                'created_at': time.time(),
                'last_activity': time.time(),
                'ip_address': user_data.get('ip_address'),
                'user_agent': user_data.get('user_agent')
            }
            
            # 缓存会话数据
            cache_key = f"{self.session_prefix}{session_id}"
            if self.cache_service.set(cache_key, session_data, ttl or self.default_ttl):
                logger.info(f"用户会话创建成功: {user_id} -> {session_id}")
                return session_id
            else:
                logger.error(f"用户会话创建失败: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"创建用户会话失败: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取用户会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据或None
        """
        try:
            cache_key = f"{self.session_prefix}{session_id}"
            session_data = self.cache_service.get(cache_key)
            
            if session_data:
                # 更新最后活动时间
                session_data['last_activity'] = time.time()
                self.cache_service.set(cache_key, session_data, ttl=self.default_ttl)
                logger.debug(f"获取用户会话: {session_id}")
                return session_data
            else:
                logger.debug(f"会话不存在或已过期: {session_id}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户会话失败: {e}")
            return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """更新用户会话
        
        Args:
            session_id: 会话ID
            updates: 要更新的数据
            
        Returns:
            bool: 是否更新成功
        """
        try:
            cache_key = f"{self.session_prefix}{session_id}"
            session_data = self.cache_service.get(cache_key)
            
            if session_data:
                # 更新数据
                session_data.update(updates)
                session_data['last_activity'] = time.time()
                
                # 重新缓存
                if self.cache_service.set(cache_key, session_data, ttl=self.default_ttl):
                    logger.debug(f"用户会话更新成功: {session_id}")
                    return True
                else:
                    logger.error(f"用户会话更新失败: {session_id}")
                    return False
            else:
                logger.warning(f"尝试更新不存在的会话: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"更新用户会话失败: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """删除用户会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            cache_key = f"{self.session_prefix}{session_id}"
            if self.cache_service.delete(cache_key):
                logger.info(f"用户会话删除成功: {session_id}")
                return True
            else:
                logger.warning(f"用户会话删除失败: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除用户会话失败: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> list:
        """获取用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 会话列表
        """
        try:
            # 获取所有会话键
            pattern = f"{self.session_prefix}*"
            keys = self.cache_service._get_redis_service().keys(pattern)
            
            sessions = []
            for key in keys:
                session_data = self.cache_service.get(key)
                if session_data and session_data.get('user_id') == user_id:
                    sessions.append(session_data)
            
            logger.debug(f"获取用户会话列表: {user_id} -> {len(sessions)} 个会话")
            return sessions
            
        except Exception as e:
            logger.error(f"获取用户会话列表失败: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话
        
        Returns:
            int: 清理的会话数量
        """
        try:
            pattern = f"{self.session_prefix}*"
            keys = self.cache_service._get_redis_service().keys(pattern)
            
            cleaned_count = 0
            current_time = time.time()
            
            for key in keys:
                session_data = self.cache_service.get(key)
                if session_data:
                    # 检查是否过期（超过默认TTL）
                    if current_time - session_data.get('last_activity', 0) > self.default_ttl:
                        if self.cache_service.delete(key):
                            cleaned_count += 1
            
            logger.info(f"清理过期会话完成: {cleaned_count} 个会话")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期会话失败: {e}")
            return 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计信息
        
        Returns:
            会话统计信息
        """
        try:
            pattern = f"{self.session_prefix}*"
            keys = self.cache_service._get_redis_service().keys(pattern)
            
            total_sessions = len(keys)
            active_sessions = 0
            current_time = time.time()
            
            for key in keys:
                session_data = self.cache_service.get(key)
                if session_data:
                    # 检查是否活跃（最近30分钟有活动）
                    if current_time - session_data.get('last_activity', 0) < 1800:
                        active_sessions += 1
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'expired_sessions': total_sessions - active_sessions
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
            return {'total_sessions': 0, 'active_sessions': 0, 'expired_sessions': 0}

# 全局会话服务实例
_session_service = None

def get_session_service() -> SessionService:
    """获取全局会话服务实例"""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service
