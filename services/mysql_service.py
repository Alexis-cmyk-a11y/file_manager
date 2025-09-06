"""
MySQL数据库服务
提供数据库连接、操作和管理功能
"""

import os
import sys
import time
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager
from datetime import datetime

try:
    import pymysql
    from pymysql.cursors import DictCursor
    from pymysql.err import OperationalError, ProgrammingError, IntegrityError
except ImportError:
    pymysql = None
    print("警告: PyMySQL未安装，MySQL功能将不可用")

from core.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

class MySQLService:
    """MySQL数据库服务类"""
    
    def __init__(self):
        self.config = Config()
        self.connection_pool = []
        self.max_connections = 20
        self.min_connections = 5
        self._initialize_pool()
    
    def _initialize_pool(self):
        """初始化连接池"""
        if not pymysql:
            logger.error("PyMySQL未安装，无法初始化MySQL连接池")
            return
        
        try:
            # 创建初始连接
            for _ in range(self.min_connections):
                conn = self._create_connection()
                if conn:
                    self.connection_pool.append(conn)
            
            logger.info(f"MySQL连接池初始化完成，当前连接数: {len(self.connection_pool)}")
        except Exception as e:
            logger.error(f"MySQL连接池初始化失败: {e}")
    
    def _create_connection(self) -> Optional[pymysql.Connection]:
        """创建新的数据库连接"""
        try:
            # 从配置文件获取MySQL配置
            logger.info(f"尝试创建MySQL连接: {self.config.MYSQL_HOST}:{self.config.MYSQL_PORT}")
            
            connection = pymysql.connect(
                host=self.config.MYSQL_HOST,
                port=self.config.MYSQL_PORT,
                user=self.config.MYSQL_USERNAME,
                password=self.config.MYSQL_PASSWORD,
                database=self.config.MYSQL_DATABASE,
                charset=self.config.MYSQL_CHARSET,
                cursorclass=DictCursor,
                autocommit=self.config.MYSQL_OPTIONS['autocommit'],
                connect_timeout=self.config.MYSQL_OPTIONS['connect_timeout'],
                read_timeout=self.config.MYSQL_OPTIONS['read_timeout'],
                write_timeout=self.config.MYSQL_OPTIONS['write_timeout']
            )
            
            # 测试连接
            connection.ping(reconnect=False)
            logger.info("MySQL连接创建成功")
            return connection
            
        except Exception as e:
            logger.error(f"创建MySQL连接失败: {e}")
            return None
    
    def _get_connection(self) -> Optional[pymysql.Connection]:
        """从连接池获取连接"""
        try:
            if not self.connection_pool:
                # 如果连接池为空，创建新连接
                conn = self._create_connection()
                if conn:
                    return conn
                # 如果创建失败，尝试再次创建
                conn = self._create_connection()
                if conn:
                    return conn
                logger.error("无法创建数据库连接")
                return None
            
            # 从连接池获取连接
            conn = self.connection_pool.pop()
            
            # 检查连接是否有效
            try:
                conn.ping(reconnect=False)
                return conn
            except Exception:
                # 连接无效，关闭并创建新连接
                try:
                    conn.close()
                except:
                    pass
                conn = self._create_connection()
                if conn:
                    return conn
                # 如果创建失败，尝试再次创建
                conn = self._create_connection()
                return conn
        except Exception as e:
            logger.error(f"获取数据库连接失败: {e}")
            return None
    
    def _return_connection(self, conn: pymysql.Connection):
        """将连接返回到连接池"""
        if conn and len(self.connection_pool) < self.max_connections:
            try:
                # 检查连接是否有效
                conn.ping(reconnect=False)
                self.connection_pool.append(conn)
            except Exception:
                # 连接无效，关闭它
                try:
                    conn.close()
                except:
                    pass
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = self._get_connection()
            if conn:
                yield conn
            else:
                raise Exception("无法获取数据库连接")
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if conn:
                self._return_connection(conn)
    
    def execute_query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute(sql, params)
                    result = cursor.fetchall()
                    logger.debug(f"执行查询成功: {sql}, 参数: {params}, 结果行数: {len(result)}")
                    return result
                except Exception as e:
                    logger.error(f"查询执行失败: {sql}, 参数: {params}, 错误: {e}")
                    raise
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    # 添加调试日志
                    logger.info(f"执行SQL: {sql}")
                    logger.info(f"参数: {params}")
                    
                    affected_rows = cursor.execute(sql, params)
                    
                    # 如果是INSERT语句，获取插入后的主键ID
                    if sql.strip().upper().startswith('INSERT'):
                        last_insert_id = cursor.lastrowid
                        conn.commit()
                        logger.info(f"执行插入成功: {sql}, 参数: {params}, 影响行数: {affected_rows}, 插入ID: {last_insert_id}")
                        return last_insert_id
                    else:
                        conn.commit()
                        logger.info(f"执行更新成功: {sql}, 参数: {params}, 影响行数: {affected_rows}")
                        return affected_rows
                except Exception as e:
                    conn.rollback()
                    logger.error(f"更新执行失败: {sql}, 参数: {params}, 错误: {e}")
                    raise
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    affected_rows = cursor.executemany(sql, params_list)
                    conn.commit()
                    logger.debug(f"批量执行成功: {sql}, 参数数量: {len(params_list)}, 影响行数: {affected_rows}")
                    return affected_rows
                except Exception as e:
                    conn.rollback()
                    logger.error(f"批量执行失败: {sql}, 参数数量: {len(params_list)}, 错误: {e}")
                    raise
    
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        sql = "SHOW TABLES LIKE %s"
        try:
            result = self.execute_query(sql, (table_name,))
            return len(result) > 0
        except Exception as e:
            logger.error(f"检查表是否存在失败: {table_name}, 错误: {e}")
            return False
    
    def create_tables(self):
        """创建必要的数据库表"""
        try:
            # 文件信息表
            if not self.table_exists('files'):
                self._create_files_table()
            
            # 文件操作日志表
            if not self.table_exists('file_operations'):
                self._create_file_operations_table()
            
            # 用户会话表
            if not self.table_exists('user_sessions'):
                self._create_user_sessions_table()
            
            # 系统配置表
            if not self.table_exists('system_configs'):
                self._create_system_configs_table()
            
            # 用户表
            if not self.table_exists('users'):
                self._create_users_table()
            
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def _create_files_table(self):
        """创建文件信息表"""
        sql = """
        CREATE TABLE IF NOT EXISTS files (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            file_path VARCHAR(1000) NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            file_size BIGINT NOT NULL,
            file_type VARCHAR(100),
            mime_type VARCHAR(200),
            hash_value VARCHAR(64),
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            modified_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_directory BOOLEAN DEFAULT FALSE,
            parent_path VARCHAR(1000),
            owner VARCHAR(100),
            INDEX idx_file_path (file_path(255)),
            INDEX idx_file_name (file_name),
            INDEX idx_created_time (created_time),
            INDEX idx_modified_time (modified_time),
            UNIQUE KEY uk_file_path (file_path)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_update(sql)
    
    def _create_file_operations_table(self):
        """创建文件操作日志表"""
        sql = """
        CREATE TABLE IF NOT EXISTS file_operations (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            operation_type ENUM('upload', 'download', 'delete', 'rename', 'move', 'copy', 'create_folder', 'list_directory', 'get_file_info', 'search', 'delete_folder', 'download_range', 'web_download', 'delete_downloaded_file', 'unknown') NOT NULL,
            file_path VARCHAR(1000),
            file_name VARCHAR(255),
            file_size BIGINT,
            user_ip VARCHAR(45),
            user_agent TEXT,
            operation_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status ENUM('success', 'failed', 'pending') DEFAULT 'success',
            error_message TEXT,
            duration_ms INT,
            INDEX idx_operation_type (operation_type),
            INDEX idx_file_path (file_path(255)),
            INDEX idx_operation_time (operation_time),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_update(sql)
    
    def _create_user_sessions_table(self):
        """创建用户会话表"""
        sql = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_ip VARCHAR(45),
            user_agent TEXT,
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_session_id (session_id),
            INDEX idx_user_ip (user_ip),
            INDEX idx_expires_at (expires_at),
            INDEX idx_is_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_update(sql)
    
    def _create_system_configs_table(self):
        """创建系统配置表"""
        sql = """
        CREATE TABLE IF NOT EXISTS system_configs (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            config_key VARCHAR(255) NOT NULL,
            config_value TEXT,
            config_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string',
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_config_key (config_key),
            INDEX idx_is_active (is_active),
            UNIQUE KEY uk_config_key (config_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_update(sql)
    
    def log_file_operation(self, operation_type: str, file_path: str = None, 
                          file_name: str = None, file_size: int = None, 
                          user_ip: str = None, user_agent: str = None,
                          status: str = 'success', error_message: str = None,
                          duration_ms: int = None):
        """记录文件操作日志"""
        sql = """
        INSERT INTO file_operations 
        (operation_type, file_path, file_name, file_size, user_ip, user_agent, status, error_message, duration_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.execute_update(sql, (
                operation_type, file_path, file_name, file_size,
                user_ip, user_agent, status, error_message, duration_ms
            ))
        except Exception as e:
            logger.error(f"记录文件操作日志失败: {e}")
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        sql = "SELECT * FROM files WHERE file_path = %s"
        try:
            result = self.execute_query(sql, (file_path,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"获取文件信息失败: {file_path}, 错误: {e}")
            return None
    
    def save_file_info(self, file_info: Dict[str, Any]) -> bool:
        """保存文件信息"""
        sql = """
        INSERT INTO files 
        (file_path, file_name, file_size, file_type, mime_type, hash_value, 
         is_directory, parent_path, owner)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        file_size = VALUES(file_size),
        modified_time = CURRENT_TIMESTAMP
        """
        try:
            # 添加调试日志
            logger.info(f"尝试保存文件信息: {file_info.get('file_path')}")
            
            result = self.execute_update(sql, (
                file_info.get('file_path'),
                file_info.get('file_name'),
                file_info.get('file_size', 0),
                file_info.get('file_type'),
                file_info.get('mime_type'),
                file_info.get('hash_value'),
                file_info.get('is_directory', False),
                file_info.get('parent_path'),
                file_info.get('owner')
            ))
            
            logger.info(f"文件信息保存成功: {file_info.get('file_path')}, 影响行数: {result}")
            return True
            
        except Exception as e:
            logger.error(f"保存文件信息失败: {file_info.get('file_path')}, 错误: {e}")
            # 重新抛出异常以便调试
            raise
    
    def delete_file_info(self, file_path: str) -> bool:
        """删除文件信息"""
        sql = "DELETE FROM files WHERE file_path = %s"
        try:
            # 添加调试日志
            logger.info(f"尝试删除文件信息: {file_path}")
            
            affected_rows = self.execute_update(sql, (file_path,))
            logger.info(f"文件信息删除成功: {file_path}, 影响行数: {affected_rows}")
            return affected_rows > 0
            
        except Exception as e:
            logger.error(f"删除文件信息失败: {file_path}, 错误: {e}")
            # 重新抛出异常以便调试
            raise
    
    def get_operation_stats(self, days: int = 7) -> Dict[str, Any]:
        """获取操作统计信息"""
        sql = """
        SELECT 
            operation_type,
            COUNT(*) as count,
            AVG(duration_ms) as avg_duration,
            SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count
        FROM file_operations 
        WHERE operation_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
        GROUP BY operation_type
        """
        try:
            result = self.execute_query(sql, (days,))
            return {
                'period_days': days,
                'operations': result,
                'total_operations': sum(op['count'] for op in result),
                'success_rate': sum(op['success_count'] for op in result) / max(sum(op['count'] for op in result), 1) * 100
            }
        except Exception as e:
            logger.error(f"获取操作统计失败: {e}")
            return {}
    
    def cleanup_old_logs(self, retention_days: int = 30) -> Dict[str, Any]:
        """清理超过保留天数的操作日志"""
        try:
            # 获取清理前的记录数
            count_sql = """
            SELECT COUNT(*) as total_count,
                   COUNT(CASE WHEN operation_time < DATE_SUB(NOW(), INTERVAL %s DAY) THEN 1 END) as old_count
            FROM file_operations
            """
            count_result = self.execute_query(count_sql, (retention_days,))
            total_count = count_result[0]['total_count'] if count_result else 0
            old_count = count_result[0]['old_count'] if count_result else 0
            
            if old_count == 0:
                return {
                    'success': True,
                    'message': f'没有超过{retention_days}天的日志需要清理',
                    'deleted_count': 0,
                    'remaining_count': total_count,
                    'retention_days': retention_days
                }
            
            # 删除超过保留天数的日志
            delete_sql = """
            DELETE FROM file_operations 
            WHERE operation_time < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            deleted_count = self.execute_update(delete_sql, (retention_days,))
            
            # 获取清理后的记录数
            remaining_count = total_count - deleted_count
            
            logger.info(f"操作日志清理完成: 删除了{deleted_count}条超过{retention_days}天的记录，剩余{remaining_count}条")
            
            return {
                'success': True,
                'message': f'成功清理{deleted_count}条超过{retention_days}天的操作日志',
                'deleted_count': deleted_count,
                'remaining_count': remaining_count,
                'retention_days': retention_days,
                'cleanup_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"清理操作日志失败: {e}")
            return {
                'success': False,
                'message': f'清理操作日志失败: {str(e)}',
                'error': str(e)
            }
    
    def get_log_retention_info(self) -> Dict[str, Any]:
        """获取日志保留信息"""
        try:
            # 获取总记录数
            total_sql = "SELECT COUNT(*) as total FROM file_operations"
            total_result = self.execute_query(total_sql)
            total_count = total_result[0]['total'] if total_result else 0
            
            # 获取各时间段的记录数
            time_ranges = [
                (1, "1天内"),
                (7, "7天内"),
                (30, "30天内"),
                (90, "90天内"),
                (365, "1年内")
            ]
            
            retention_stats = {}
            for days, label in time_ranges:
                sql = """
                SELECT COUNT(*) as count
                FROM file_operations 
                WHERE operation_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
                """
                result = self.execute_query(sql, (days,))
                count = result[0]['count'] if result else 0
                retention_stats[label] = count
            
            # 获取最早的日志时间
            oldest_sql = "SELECT MIN(operation_time) as oldest_time FROM file_operations"
            oldest_result = self.execute_query(oldest_sql)
            oldest_time = oldest_result[0]['oldest_time'] if oldest_result and oldest_result[0]['oldest_time'] else None
            
            # 获取最新的日志时间
            newest_sql = "SELECT MAX(operation_time) as newest_time FROM file_operations"
            newest_result = self.execute_query(newest_sql)
            newest_time = newest_result[0]['newest_time'] if newest_result and newest_result[0]['newest_time'] else None
            
            return {
                'success': True,
                'total_records': total_count,
                'retention_stats': retention_stats,
                'oldest_log_time': oldest_time.isoformat() if oldest_time else None,
                'newest_log_time': newest_time.isoformat() if newest_time else None,
                'current_time': datetime.now().isoformat(),
                'recommended_cleanup': total_count > 10000  # 如果超过1万条记录建议清理
            }
            
        except Exception as e:
            logger.error(f"获取日志保留信息失败: {e}")
            return {
                'success': False,
                'message': f'获取日志保留信息失败: {str(e)}',
                'error': str(e)
            }
    
    def optimize_log_table(self) -> Dict[str, Any]:
        """优化日志表性能"""
        try:
            # 获取表状态信息
            status_sql = "SHOW TABLE STATUS LIKE 'file_operations'"
            status_result = self.execute_query(status_sql)
            
            if not status_result:
                return {
                    'success': False,
                    'message': '无法获取表状态信息'
                }
            
            table_info = status_result[0]
            data_length = table_info.get('Data_length', 0)
            index_length = table_info.get('Index_length', 0)
            data_free = table_info.get('Data_free', 0)
            
            # 如果存在碎片，进行优化
            if data_free > 0:
                optimize_sql = "OPTIMIZE TABLE file_operations"
                self.execute_update(optimize_sql)
                
                logger.info("日志表优化完成，清理了表碎片")
                
                return {
                    'success': True,
                    'message': '日志表优化完成',
                    'data_length_mb': round(data_length / 1024 / 1024, 2),
                    'index_length_mb': round(index_length / 1024 / 1024, 2),
                    'fragmented_space_mb': round(data_free / 1024 / 1024, 2),
                    'optimization_time': datetime.now().isoformat()
                }
            else:
                return {
                    'success': True,
                    'message': '日志表无需优化，没有碎片',
                    'data_length_mb': round(data_length / 1024 / 1024, 2),
                    'index_length_mb': round(index_length / 1024 / 1024, 2),
                    'fragmented_space_mb': 0
                }
                
        except Exception as e:
            logger.error(f"优化日志表失败: {e}")
            return {
                'success': False,
                'message': f'优化日志表失败: {str(e)}',
                'error': str(e)
            }
    
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception:
            return False
    
    def close_all_connections(self):
        """关闭所有数据库连接"""
        for conn in self.connection_pool:
            try:
                conn.close()
            except:
                pass
        self.connection_pool.clear()
        logger.info("所有MySQL连接已关闭")
    
    def _create_users_table(self):
        """创建用户表"""
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('user', 'admin') DEFAULT 'user',
            status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME NULL,
            INDEX idx_email (email),
            INDEX idx_status (status),
            INDEX idx_role (role),
            UNIQUE KEY uk_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        self.execute_update(sql)
        logger.info("用户表创建成功")
    
    def user_exists(self, email: str) -> bool:
        """检查用户是否存在"""
        sql = "SELECT COUNT(*) as count FROM users WHERE email = %s"
        try:
            result = self.execute_query(sql, (email,))
            return result[0]['count'] > 0 if result else False
        except Exception as e:
            logger.error(f"检查用户是否存在失败: {email}, 错误: {e}")
            return False
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[int]:
        """创建用户"""
        sql = """
        INSERT INTO users (email, password_hash, role, status, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            user_id = self.execute_update(sql, (
                user_data['email'],
                user_data['password_hash'],
                user_data.get('role', 'user'),
                user_data.get('status', 'active'),
                user_data['created_at']
            ))
            logger.info(f"用户创建成功: {user_data['email']}, 用户ID: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"创建用户失败: {user_data['email']}, 错误: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户信息"""
        sql = "SELECT * FROM users WHERE email = %s"
        try:
            result = self.execute_query(sql, (email,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"根据邮箱获取用户信息失败: {email}, 错误: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        sql = "SELECT * FROM users WHERE id = %s"
        try:
            result = self.execute_query(sql, (user_id,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"根据ID获取用户信息失败: {user_id}, 错误: {e}")
            return None
    
    def update_user_last_login(self, user_id: int) -> bool:
        """更新用户最后登录时间"""
        sql = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
        try:
            affected_rows = self.execute_update(sql, (user_id,))
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新用户最后登录时间失败: {user_id}, 错误: {e}")
            return False
    
    def update_user_password(self, user_id: int, password_hash: str) -> bool:
        """更新用户密码"""
        sql = "UPDATE users SET password_hash = %s WHERE id = %s"
        try:
            affected_rows = self.execute_update(sql, (password_hash, user_id))
            return affected_rows > 0
        except Exception as e:
            logger.error(f"更新用户密码失败: {user_id}, 错误: {e}")
            return False
    
    def get_current_time(self):
        """获取当前数据库时间"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT NOW() as current_time")
                    result = cursor.fetchone()
                    return result['current_time']
        except Exception as e:
            logger.error(f"获取数据库当前时间失败: {e}")
            # 如果数据库时间获取失败，返回Python当前时间
            from datetime import datetime
            return datetime.now()

# 全局MySQL服务实例
_mysql_service = None

def get_mysql_service() -> MySQLService:
    """获取MySQL服务实例"""
    global _mysql_service
    if _mysql_service is None:
        _mysql_service = MySQLService()
    return _mysql_service

def close_mysql_service():
    """关闭MySQL服务"""
    global _mysql_service
    if _mysql_service:
        _mysql_service.close_all_connections()
        _mysql_service = None
