"""
日志维护服务
提供自动清理过期日志、优化表性能等功能
"""

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from core.config import Config
from services.mysql_service import get_mysql_service
from utils.logger import get_logger

logger = get_logger(__name__)

class LogMaintenanceService:
    """日志维护服务类"""
    
    def __init__(self):
        self.config = Config()
        self.mysql_service = None
        self.maintenance_thread = None
        self.running = False
        self.last_cleanup = None
        self.last_optimize = None
        
        # 初始化MySQL服务
        try:
            self.mysql_service = get_mysql_service()
        except Exception as e:
            logger.error(f"初始化日志维护服务失败: {e}")
    
    def start_auto_maintenance(self):
        """启动自动维护服务"""
        if not self.config.MYSQL_LOG_RETENTION['enabled']:
            logger.info("日志自动维护已禁用")
            return False
        
        if not self.mysql_service or not self.mysql_service.is_connected():
            logger.error("MySQL服务不可用，无法启动自动维护")
            return False
        
        if self.running:
            logger.info("自动维护服务已在运行")
            return True
        
        try:
            self.running = True
            self.maintenance_thread = threading.Thread(
                target=self._maintenance_worker,
                daemon=True,
                name="LogMaintenanceWorker"
            )
            self.maintenance_thread.start()
            
            logger.info("日志自动维护服务已启动")
            return True
            
        except Exception as e:
            logger.error(f"启动自动维护服务失败: {e}")
            self.running = False
            return False
    
    def stop_auto_maintenance(self):
        """停止自动维护服务"""
        if not self.running:
            return
        
        self.running = False
        if self.maintenance_thread:
            self.maintenance_thread.join(timeout=5)
        
        logger.info("日志自动维护服务已停止")
    
    def _maintenance_worker(self):
        """维护工作线程"""
        logger.info("日志维护工作线程已启动")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # 检查是否需要清理日志
                if self._should_cleanup_logs(current_time):
                    self._perform_log_cleanup()
                
                # 检查是否需要优化表
                if self._should_optimize_table(current_time):
                    self._perform_table_optimization()
                
                # 休眠1小时
                time.sleep(3600)
                
            except Exception as e:
                logger.error(f"维护工作线程执行失败: {e}")
                time.sleep(300)  # 出错后等待5分钟再重试
        
        logger.info("日志维护工作线程已退出")
    
    def _should_cleanup_logs(self, current_time: datetime) -> bool:
        """检查是否需要清理日志"""
        # 如果从未清理过，或者距离上次清理超过24小时
        if not self.last_cleanup:
            return True
        
        time_since_last_cleanup = current_time - self.last_cleanup
        return time_since_last_cleanup.total_seconds() >= 24 * 3600  # 24小时
    
    def _should_optimize_table(self, current_time: datetime) -> bool:
        """检查是否需要优化表"""
        # 如果从未优化过，或者距离上次优化超过7天
        if not self.last_optimize:
            return True
        
        time_since_last_optimize = current_time - self.last_optimize
        return time_since_last_optimize.total_seconds() >= 7 * 24 * 3600  # 7天
    
    def _perform_log_cleanup(self):
        """执行日志清理"""
        try:
            retention_days = self.config.MYSQL_LOG_RETENTION['retention_days']
            logger.info(f"开始自动清理超过{retention_days}天的操作日志")
            
            cleanup_result = self.mysql_service.cleanup_old_logs(retention_days)
            
            if cleanup_result.get('success'):
                deleted_count = cleanup_result.get('deleted_count', 0)
                if deleted_count > 0:
                    logger.info(f"自动清理完成: 删除了{deleted_count}条过期日志")
                else:
                    logger.info("自动清理完成: 没有需要清理的日志")
                
                self.last_cleanup = datetime.now()
            else:
                logger.error(f"自动清理失败: {cleanup_result.get('message')}")
                
        except Exception as e:
            logger.error(f"执行日志清理失败: {e}")
    
    def _perform_table_optimization(self):
        """执行表优化"""
        try:
            logger.info("开始自动优化日志表")
            
            optimize_result = self.mysql_service.optimize_log_table()
            
            if optimize_result.get('success'):
                fragmented_space = optimize_result.get('fragmented_space_mb', 0)
                if fragmented_space > 0:
                    logger.info(f"表优化完成: 清理了{fragmented_space}MB碎片空间")
                else:
                    logger.info("表优化完成: 没有碎片需要清理")
                
                self.last_optimize = datetime.now()
            else:
                logger.error(f"表优化失败: {optimize_result.get('message')}")
                
        except Exception as e:
            logger.error(f"执行表优化失败: {e}")
    
    def manual_cleanup(self, retention_days: Optional[int] = None) -> Dict[str, Any]:
        """手动清理日志"""
        try:
            if not retention_days:
                retention_days = self.config.MYSQL_LOG_RETENTION['retention_days']
            
            logger.info(f"开始手动清理超过{retention_days}天的操作日志")
            
            cleanup_result = self.mysql_service.cleanup_old_logs(retention_days)
            
            if cleanup_result.get('success'):
                self.last_cleanup = datetime.now()
                logger.info("手动清理完成")
            else:
                logger.error(f"手动清理失败: {cleanup_result.get('message')}")
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"手动清理失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def manual_optimize(self) -> Dict[str, Any]:
        """手动优化表"""
        try:
            logger.info("开始手动优化日志表")
            
            optimize_result = self.mysql_service.optimize_log_table()
            
            if optimize_result.get('success'):
                self.last_optimize = datetime.now()
                logger.info("手动优化完成")
            else:
                logger.error(f"手动优化失败: {optimize_result.get('message')}")
            
            return optimize_result
            
        except Exception as e:
            logger.error(f"手动优化失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_maintenance_status(self) -> Dict[str, Any]:
        """获取维护服务状态"""
        return {
            'running': self.running,
            'last_cleanup': self.last_cleanup.isoformat() if self.last_cleanup else None,
            'last_optimize': self.last_optimize.isoformat() if self.last_optimize else None,
            'config': {
                'enabled': self.config.MYSQL_LOG_RETENTION['enabled'],
                'retention_days': self.config.MYSQL_LOG_RETENTION['retention_days'],
                'auto_cleanup': self.config.MYSQL_LOG_RETENTION['auto_cleanup'],
                'max_records': self.config.MYSQL_LOG_RETENTION['max_records']
            }
        }
    
    def is_healthy(self) -> bool:
        """检查服务健康状态"""
        if not self.running:
            return False
        
        if not self.mysql_service or not self.mysql_service.is_connected():
            return False
        
        return True

# 全局日志维护服务实例
_log_maintenance_service = None

def get_log_maintenance_service() -> LogMaintenanceService:
    """获取日志维护服务实例"""
    global _log_maintenance_service
    if _log_maintenance_service is None:
        _log_maintenance_service = LogMaintenanceService()
    return _log_maintenance_service

def start_log_maintenance():
    """启动日志维护服务"""
    service = get_log_maintenance_service()
    return service.start_auto_maintenance()

def stop_log_maintenance():
    """停止日志维护服务"""
    service = get_log_maintenance_service()
    service.stop_auto_maintenance()
