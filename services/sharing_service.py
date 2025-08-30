#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件共享服务
基于硬链接实现文件共享，用户可以在共享区查看和下载文件
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Tuple
from services.mysql_service import get_mysql_service
from utils.logger import get_logger

logger = get_logger(__name__)

class SharingService:
    """文件共享服务"""
    
    def __init__(self):
        self.mysql_service = get_mysql_service()
        self.shared_base_dir = os.path.join('home', 'shared')
        self.users_base_dir = os.path.join('home', 'users')  # 用户目录在home/users下
    
    def share_file(self, username: str, file_path: str, target_name: str = None) -> Tuple[bool, str]:
        """
        共享文件
        :param username: 用户名
        :param file_path: 文件路径（相对于用户目录）
        :param target_name: 目标文件名（可选，默认使用原文件名）
        :return: (成功标志, 消息)
        """
        try:
            # 首先尝试相对于当前工作目录的路径
            full_file_path = os.path.abspath(file_path)
            logger.info(f"尝试共享文件，用户名: {username}, 文件路径: {file_path}")
            logger.info(f"构建的完整路径: {full_file_path}")
            logger.info(f"当前工作目录: {os.getcwd()}")
            
            # 如果文件不存在，尝试相对于用户目录的路径
            if not os.path.exists(full_file_path):
                user_file_path = os.path.join(self.users_base_dir, username, file_path)
                logger.info(f"尝试用户目录路径: {user_file_path}")
                if os.path.exists(user_file_path):
                    full_file_path = user_file_path
                else:
                    logger.info(f"文件不存在: {full_file_path}")
                    return False, "文件不存在"
            
            # 创建共享目录
            shared_dir = os.path.join(self.shared_base_dir, f'{username}_shared')
            os.makedirs(shared_dir, exist_ok=True)
            
            # 使用目标名称或原文件名
            final_target_name = target_name if target_name else os.path.basename(file_path)
            shared_file_path = os.path.join(shared_dir, final_target_name)
            
            # 如果共享文件已存在，先删除
            if os.path.exists(shared_file_path):
                os.remove(shared_file_path)
            
            # 创建硬链接
            os.link(full_file_path, shared_file_path)
            
            # 设置共享文件权限为只读
            os.chmod(shared_file_path, 0o644)
            
            # 记录到数据库
            self._record_shared_file(username, full_file_path, shared_file_path)
            
            logger.info(f"用户 {username} 成功共享文件: {file_path} -> {final_target_name}")
            return True, "文件共享成功"
            
        except Exception as e:
            logger.error(f"共享文件失败: {e}")
            return False, f"共享失败: {str(e)}"
    
    def unshare_file(self, username: str, file_path: str) -> Tuple[bool, str]:
        """
        取消共享文件
        :param username: 用户名
        :param file_path: 文件路径（相对于用户目录）
        :return: (成功标志, 消息)
        """
        try:
            # 查找共享文件
            shared_file_path = os.path.join(self.shared_base_dir, f'{username}_shared', os.path.basename(file_path))
            
            if not os.path.exists(shared_file_path):
                # 如果共享文件不存在，检查数据库记录并清理
                self._remove_shared_file(shared_file_path)
                return True, "共享文件已不存在，已清理数据库记录"
            
            try:
                # 删除共享文件（硬链接）
                os.remove(shared_file_path)
                logger.info(f"成功删除共享文件: {shared_file_path}")
            except OSError as e:
                # 如果删除失败（可能是原文件已被删除），记录日志但继续处理
                logger.warning(f"删除共享文件失败，可能原文件已被删除: {shared_file_path}, 错误: {e}")
            
            # 从数据库移除记录
            self._remove_shared_file(shared_file_path)
            
            logger.info(f"用户 {username} 成功取消共享文件: {file_path}")
            return True, "取消共享成功"
            
        except Exception as e:
            logger.error(f"取消共享文件失败: {e}")
            return False, f"取消共享失败: {str(e)}"
    
    def delete_shared_file(self, username: str, filename: str) -> Tuple[bool, str]:
        """
        直接从共享目录删除文件
        :param username: 用户名
        :param filename: 文件名
        :return: (成功标志, 消息)
        """
        try:
            # 构建共享文件路径
            shared_file_path = os.path.join(self.shared_base_dir, f'{username}_shared', filename)
            
            if not os.path.exists(shared_file_path):
                # 如果文件不存在，清理数据库记录
                self._remove_shared_file(shared_file_path)
                return True, "文件已不存在，已清理数据库记录"
            
            try:
                # 删除共享文件
                os.remove(shared_file_path)
                logger.info(f"成功删除共享文件: {shared_file_path}")
            except OSError as e:
                # 如果删除失败，记录错误但继续处理
                logger.error(f"删除共享文件失败: {shared_file_path}, 错误: {e}")
                return False, f"删除文件失败: {str(e)}"
            
            # 从数据库移除记录
            self._remove_shared_file(shared_file_path)
            
            logger.info(f"用户 {username} 成功删除共享文件: {filename}")
            return True, "删除成功"
            
        except Exception as e:
            logger.error(f"删除共享文件失败: {e}")
            return False, f"删除失败: {str(e)}"
    
    def get_shared_files(self, username: str = None) -> List[Dict[str, str]]:
        """
        获取共享文件列表
        :param username: 用户名，如果为None则返回所有共享文件
        :return: 共享文件列表
        """
        try:
            if username:
                # 获取特定用户的共享文件
                shared_dir = os.path.join(self.shared_base_dir, f'{username}_shared')
                if not os.path.exists(shared_dir):
                    return []
                
                shared_files = []
                for filename in os.listdir(shared_dir):
                    file_path = os.path.join(shared_dir, filename)
                    if os.path.isfile(file_path):
                        shared_files.append({
                            'name': filename,
                            'path': f'{username}_shared/{filename}',
                            'size': os.path.getsize(file_path),
                            'owner': username,
                            'shared_path': file_path,
                            'is_directory': False,
                            'modified_time': os.path.getmtime(file_path)
                        })
                return shared_files
            else:
                # 获取所有共享文件
                all_shared_files = []
                for item in os.listdir(self.shared_base_dir):
                    if item.endswith('_shared') and os.path.isdir(os.path.join(self.shared_base_dir, item)):
                        owner = item.replace('_shared', '')  # 移除 '_shared' 后缀
                        # 直接获取该用户的共享文件，避免递归调用
                        shared_dir = os.path.join(self.shared_base_dir, item)
                        if os.path.exists(shared_dir):
                            for filename in os.listdir(shared_dir):
                                file_path = os.path.join(shared_dir, filename)
                                if os.path.isfile(file_path):
                                    all_shared_files.append({
                                        'name': filename,
                                        'path': f'{owner}_shared/{filename}',
                                        'size': os.path.getsize(file_path),
                                        'owner': owner,
                                        'shared_path': file_path,
                                        'is_directory': False,
                                        'modified_time': os.path.getmtime(file_path)
                                    })
                return all_shared_files
                
        except Exception as e:
            logger.error(f"获取共享文件列表失败: {e}")
            return []
    
    def is_file_shared(self, username: str, file_path: str) -> bool:
        """
        检查文件是否已共享
        :param username: 用户名
        :param file_path: 文件路径
        :return: 是否已共享
        """
        try:
            shared_file_path = os.path.join(self.shared_base_dir, f'{username}_shared', os.path.basename(file_path))
            return os.path.exists(shared_file_path)
        except Exception as e:
            logger.error(f"检查文件共享状态失败: {e}")
            return False
    
    def _record_shared_file(self, username: str, original_path: str, shared_path: str) -> None:
        """记录共享文件到数据库"""
        try:
            sql = """
            INSERT INTO shared_files (original_file_path, shared_file_path, owner_username) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            original_file_path = VALUES(original_file_path),
            is_active = TRUE
            """
            self.mysql_service.execute_update(sql, (original_path, shared_path, username))
        except Exception as e:
            logger.error(f"记录共享文件到数据库失败: {e}")
    
    def _remove_shared_file(self, shared_path: str) -> None:
        """从数据库移除共享文件记录"""
        try:
            sql = "UPDATE shared_files SET is_active = FALSE WHERE shared_file_path = %s"
            self.mysql_service.execute_update(sql, (shared_path,))
        except Exception as e:
            logger.error(f"从数据库移除共享文件记录失败: {e}")
    
    def cleanup_orphaned_shares(self) -> int:
        """
        清理孤立的共享文件（原文件已删除）
        :return: 清理的文件数量
        """
        try:
            cleaned_count = 0
            shared_files = self.get_shared_files()
            
            for shared_file in shared_files:
                shared_path = shared_file['shared_path']
                if not os.path.exists(shared_path):
                    # 共享文件不存在，清理数据库记录
                    self._remove_shared_file(shared_path)
                    cleaned_count += 1
                    logger.info(f"清理孤立的共享文件记录: {shared_path}")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理孤立共享文件失败: {e}")
            return 0

# 全局实例
_sharing_service = None

def get_sharing_service() -> SharingService:
    """获取共享服务实例"""
    global _sharing_service
    if _sharing_service is None:
        _sharing_service = SharingService()
    return _sharing_service
