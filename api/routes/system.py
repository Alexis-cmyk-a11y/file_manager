"""
系统监控API路由
提供系统状态、性能监控、健康检查等功能
"""

from flask import Blueprint, jsonify, current_app, request
from datetime import datetime
import os
import psutil
import platform
from services.redis_service import get_redis_service
from services.cache_service import get_cache_service
from utils.performance_monitor import get_performance_monitor
from utils.logger import get_logger

bp = Blueprint('system', __name__, url_prefix='/api')

logger = get_logger(__name__)

@bp.route('/health', methods=['GET'])
def health_check():
    """系统健康检查"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'services': {},
            'system': {},
            'performance': {}
        }
        
        # 检查Redis服务
        try:
            redis_service = get_redis_service()
            redis_healthy = redis_service.is_connected() if redis_service else False
            health_status['services']['redis'] = {
                'status': 'healthy' if redis_healthy else 'unhealthy',
                'connected': redis_healthy,
                'host': current_app.config.get('REDIS_HOST', 'localhost'),
                'port': current_app.config.get('REDIS_PORT', 6379)
            }
        except Exception as e:
            health_status['services']['redis'] = {
                'status': 'error',
                'connected': False,
                'error': str(e)
            }
        
        # 检查缓存服务
        try:
            cache_service = get_cache_service()
            cache_stats = cache_service.get_stats()
            health_status['services']['cache'] = {
                'status': 'healthy',
                'memory_cache': cache_stats.get('memory_cache', {}),
                'redis_cache': cache_stats.get('redis_cache', {})
            }
        except Exception as e:
            health_status['services']['cache'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 检查文件系统
        try:
            root_dir = current_app.config.get('ROOT_DIR', '.')
            disk_usage = get_disk_usage(root_dir)
            health_status['services']['file_system'] = {
                'status': 'healthy',
                'root_directory': root_dir,
                'exists': os.path.exists(root_dir),
                'readable': os.access(root_dir, os.R_OK),
                'writable': os.access(root_dir, os.W_OK),
                'disk_usage': disk_usage
            }
        except Exception as e:
            health_status['services']['file_system'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 系统信息
        try:
            health_status['system'] = get_system_info()
        except Exception as e:
            health_status['system'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 性能信息
        try:
            performance_monitor = get_performance_monitor()
            health_status['performance'] = {
                'status': 'healthy',
                'monitoring_enabled': current_app.config.get('ENABLE_PERFORMANCE_MONITORING', True),
                'total_functions': len(performance_monitor.get_all_stats()),
                'slow_functions_count': len(performance_monitor.get_slow_functions())
            }
        except Exception as e:
            health_status['performance'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # 检查整体健康状态
        all_services = health_status['services'].values()
        if any(service.get('status') == 'error' for service in all_services):
            health_status['status'] = 'degraded'
        elif any(service.get('status') == 'unhealthy' for service in all_services):
            health_status['status'] = 'unhealthy'
        
        # 设置HTTP状态码
        status_code = 200
        if health_status['status'] == 'unhealthy':
            status_code = 503
        elif health_status['status'] == 'degraded':
            status_code = 200  # 降级状态仍然返回200，但状态为degraded
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@bp.route('/status', methods=['GET'])
def system_status():
    """获取系统状态信息"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'system': get_system_info(),
            'application': get_application_info(),
            'resources': get_resource_usage(),
            'cache': get_cache_status(),
            'performance': get_performance_status()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/performance', methods=['GET'])
def performance_status():
    """获取性能监控状态"""
    try:
        performance_monitor = get_performance_monitor()
        
        # 获取性能报告
        report = performance_monitor.get_performance_report()
        
        # 添加实时统计
        report['real_time'] = {
            'monitoring_enabled': current_app.config.get('ENABLE_PERFORMANCE_MONITORING', True),
            'slow_threshold': current_app.config.get('PERFORMANCE_SLOW_THRESHOLD', 1.0),
            'total_metrics': sum(len(monitor.metrics[func]) for func in monitor.metrics)
        }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"获取性能状态失败: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/performance/reset', methods=['POST'])
def reset_performance_stats():
    """重置性能统计"""
    try:
        function_name = request.json.get('function_name') if request.is_json else None
        
        performance_monitor = get_performance_monitor()
        performance_monitor.reset_stats(function_name)
        
        return jsonify({
            'success': True,
            'message': f"性能统计已重置: {function_name or '所有函数'}"
        })
        
    except Exception as e:
        logger.error(f"重置性能统计失败: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/cache/status', methods=['GET'])
def cache_status():
    """获取缓存状态"""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'cache_enabled': current_app.config.get('CACHE_ENABLED', True),
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """清理缓存"""
    try:
        pattern = request.json.get('pattern', '*') if request.is_json else '*'
        
        cache_service = get_cache_service()
        cleared_count = cache_service.clear_pattern(pattern)
        
        return jsonify({
            'success': True,
            'message': f"缓存清理完成",
            'pattern': pattern,
            'cleared_count': cleared_count
        })
        
    except Exception as e:
        logger.error(f"清理缓存失败: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/logs', methods=['GET'])
def get_logs():
    """获取最近的日志信息"""
    try:
        # 这里可以实现日志查询功能
        # 目前返回基本信息
        log_config = {
            'log_level': current_app.config.get('LOG_LEVEL', 'INFO'),
            'log_file': current_app.config.get('LOG_FILE', 'logs/file_manager.log'),
            'log_format': current_app.config.get('LOG_FORMAT', 'json'),
            'log_enable_console': current_app.config.get('LOG_ENABLE_CONSOLE', True),
            'log_enable_file': current_app.config.get('LOG_ENABLE_FILE', True)
        }
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'log_config': log_config,
            'message': '日志查询功能待实现'
        })
        
    except Exception as e:
        logger.error(f"获取日志信息失败: {e}")
        return jsonify({'error': str(e)}), 500

def get_system_info():
    """获取系统信息"""
    try:
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'uptime': get_system_uptime()
        }
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return {'error': str(e)}

def get_application_info():
    """获取应用信息"""
    try:
        return {
            'app_name': current_app.config.get('APP_NAME', '文件管理系统'),
            'version': '2.0.0',
            'environment': current_app.config.get('ENV', 'production'),
            'debug_mode': current_app.config.get('DEBUG_MODE', False),
            'server_host': current_app.config.get('SERVER_HOST', '0.0.0.0'),
            'server_port': current_app.config.get('SERVER_PORT', 8888),
            'root_directory': current_app.config.get('ROOT_DIR', '.'),
            'max_file_size': current_app.config.get('MAX_FILE_SIZE', 0),
            'rate_limit': current_app.config.get('RATE_LIMIT', '100 per minute')
        }
    except Exception as e:
        logger.error(f"获取应用信息失败: {e}")
        return {'error': str(e)}

def get_resource_usage():
    """获取资源使用情况"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        root_dir = current_app.config.get('ROOT_DIR', '.')
        disk_usage = get_disk_usage(root_dir)
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True)
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free
            },
            'disk': disk_usage
        }
    except Exception as e:
        logger.error(f"获取资源使用情况失败: {e}")
        return {'error': str(e)}

def get_cache_status():
    """获取缓存状态"""
    try:
        cache_service = get_cache_service()
        stats = cache_service.get_stats()
        
        return {
            'enabled': current_app.config.get('CACHE_ENABLED', True),
            'default_ttl': current_app.config.get('CACHE_DEFAULT_TTL', 300),
            'max_items': current_app.config.get('CACHE_MAX_ITEMS', 10000),
            'stats': stats
        }
    except Exception as e:
        logger.error(f"获取缓存状态失败: {e}")
        return {'error': str(e)}

def get_performance_status():
    """获取性能状态"""
    try:
        performance_monitor = get_performance_monitor()
        
        return {
            'enabled': current_app.config.get('ENABLE_PERFORMANCE_MONITORING', True),
            'slow_threshold': current_app.config.get('PERFORMANCE_SLOW_THRESHOLD', 1.0),
            'total_functions': len(performance_monitor.get_all_stats()),
            'slow_functions': len(performance_monitor.get_slow_functions())
        }
    except Exception as e:
        logger.error(f"获取性能状态失败: {e}")
        return {'error': str(e)}

def get_disk_usage(path):
    """获取磁盘使用情况"""
    try:
        if not os.path.exists(path):
            return {'error': '路径不存在'}
        
        # 获取磁盘分区信息
        disk_partition = psutil.disk_usage(path)
        
        return {
            'total': disk_partition.total,
            'used': disk_partition.used,
            'free': disk_partition.free,
            'percent': disk_partition.percent
        }
    except Exception as e:
        return {'error': str(e)}

def get_system_uptime():
    """获取系统运行时间"""
    try:
        uptime_seconds = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(uptime_seconds)
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': uptime.total_seconds()
        }
    except Exception as e:
        return {'error': str(e)}
