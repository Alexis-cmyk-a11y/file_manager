"""
系统信息API路由
提供系统状态、配置信息等接口
"""

from flask import Blueprint, jsonify, request
from services.system_service import SystemService
from services.redis_service import get_redis_service
from services.session_service import get_session_service
from utils.logger import get_logger

bp = Blueprint('system', __name__, url_prefix='/api/system')
logger = get_logger('system_routes')
system_service = SystemService()
session_service = get_session_service()

@bp.route('/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        info = system_service.get_system_info()
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        logger.error(f"获取系统信息失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/redis/status', methods=['GET'])
def get_redis_status():
    """获取Redis状态"""
    try:
        redis_service = get_redis_service()
        if redis_service and redis_service.is_connected():
            info = redis_service.info()
            status = {
                'connected': True,
                'host': redis_service.config.REDIS_HOST,
                'port': redis_service.config.REDIS_PORT,
                'db': redis_service.config.REDIS_DB,
                'version': info.get('redis_version', 'unknown'),
                'used_memory': info.get('used_memory_human', 'unknown'),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0)
            }
            return jsonify({'success': True, 'data': status})
        else:
            return jsonify({'success': False, 'message': 'Redis未连接', 'data': {'connected': False}})
    except Exception as e:
        logger.error(f"获取Redis状态失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/redis/test', methods=['POST'])
def test_redis_connection():
    """测试Redis连接"""
    try:
        redis_service = get_redis_service()
        if redis_service and redis_service.is_connected():
            # 测试基本操作
            test_key = 'test_connection'
            test_value = {'test': True, 'timestamp': system_service.get_current_timestamp()}
            
            # 设置测试值
            if redis_service.set(test_key, test_value, ex=60):
                # 获取测试值
                retrieved_value = redis_service.get(test_key)
                if retrieved_value == test_value:
                    # 删除测试值
                    redis_service.delete(test_key)
                    return jsonify({'success': True, 'message': 'Redis连接测试成功'})
                else:
                    return jsonify({'success': False, 'message': 'Redis数据一致性测试失败'})
            else:
                return jsonify({'success': False, 'message': 'Redis写入测试失败'})
        else:
            return jsonify({'success': False, 'message': 'Redis未连接'})
    except Exception as e:
        logger.error(f"Redis连接测试失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/redis/keys', methods=['GET'])
def get_redis_keys():
    """获取Redis键列表"""
    try:
        pattern = request.args.get('pattern', '*')
        redis_service = get_redis_service()
        if redis_service and redis_service.is_connected():
            keys = redis_service.keys(pattern)
            return jsonify({'success': True, 'data': keys})
        else:
            return jsonify({'success': False, 'message': 'Redis未连接'})
    except Exception as e:
        logger.error(f"获取Redis键列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/redis/clear', methods=['POST'])
def clear_redis_database():
    """清空Redis数据库"""
    try:
        redis_service = get_redis_service()
        if redis_service and redis_service.is_connected():
            if redis_service.flushdb():
                return jsonify({'success': True, 'message': 'Redis数据库已清空'})
            else:
                return jsonify({'success': False, 'message': '清空Redis数据库失败'})
        else:
            return jsonify({'success': False, 'message': 'Redis未连接'})
    except Exception as e:
        logger.error(f"清空Redis数据库失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 会话管理端点
@bp.route('/sessions/create', methods=['POST'])
def create_user_session():
    """创建用户会话"""
    try:
        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        user_id = data['user_id']
        user_data = data.get('user_data', {})
        ttl = data.get('ttl', 3600)  # 默认1小时
        
        # 添加请求信息
        user_data.update({
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        })
        
        session_id = session_service.create_session(user_id, user_data, ttl)
        if session_id:
            return jsonify({
                'success': True, 
                'message': '会话创建成功',
                'data': {'session_id': session_id}
            })
        else:
            return jsonify({'success': False, 'message': '会话创建失败'}), 500
            
    except Exception as e:
        logger.error(f"创建用户会话失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/<session_id>', methods=['GET'])
def get_user_session(session_id):
    """获取用户会话"""
    try:
        session_data = session_service.get_session(session_id)
        if session_data:
            return jsonify({
                'success': True,
                'data': session_data
            })
        else:
            return jsonify({'success': False, 'message': '会话不存在或已过期'}), 404
            
    except Exception as e:
        logger.error(f"获取用户会话失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/<session_id>', methods=['PUT'])
def update_user_session(session_id):
    """更新用户会话"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '缺少更新数据'}), 400
        
        if session_service.update_session(session_id, data):
            return jsonify({'success': True, 'message': '会话更新成功'})
        else:
            return jsonify({'success': False, 'message': '会话更新失败'}), 500
            
    except Exception as e:
        logger.error(f"更新用户会话失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/<session_id>', methods=['DELETE'])
def delete_user_session(session_id):
    """删除用户会话"""
    try:
        if session_service.delete_session(session_id):
            return jsonify({'success': True, 'message': '会话删除成功'})
        else:
            return jsonify({'success': False, 'message': '会话删除失败'}), 500
            
    except Exception as e:
        logger.error(f"删除用户会话失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/user/<user_id>', methods=['GET'])
def get_user_sessions(user_id):
    """获取用户的所有会话"""
    try:
        sessions = session_service.get_user_sessions(user_id)
        return jsonify({
            'success': True,
            'data': {'sessions': sessions, 'count': len(sessions)}
        })
        
    except Exception as e:
        logger.error(f"获取用户会话列表失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/stats', methods=['GET'])
def get_session_stats():
    """获取会话统计信息"""
    try:
        stats = session_service.get_session_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取会话统计失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/sessions/cleanup', methods=['POST'])
def cleanup_expired_sessions():
    """清理过期会话"""
    try:
        cleaned_count = session_service.cleanup_expired_sessions()
        return jsonify({
            'success': True,
            'message': f'清理完成，共清理 {cleaned_count} 个过期会话',
            'data': {'cleaned_count': cleaned_count}
        })
        
    except Exception as e:
        logger.error(f"清理过期会话失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
