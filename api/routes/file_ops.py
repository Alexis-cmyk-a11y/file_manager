"""
文件操作API路由
包含文件列表、复制、移动、删除、重命名、创建文件夹等操作
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter.util import get_remote_address

from services.file_service import FileService
from services.security_service import SecurityService
from utils.logger import get_logger
from utils.auth_middleware import require_auth_api, get_current_user

logger = get_logger(__name__)
bp = Blueprint('file_ops', __name__, url_prefix='/api')

def get_user_info():
    """获取用户信息"""
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return user_ip, user_agent

@bp.route('/list', methods=['GET'])
@require_auth_api
def list_directory():
    """列出目录内容（需要读取权限）"""
    try:
        directory_path = request.args.get('path', '.')
        # 处理前端传递的空字符串
        if directory_path == '':
            directory_path = '.'
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 列出目录: {directory_path}")
        
        file_service = FileService()
        result = file_service.list_directory(directory_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"列出目录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/info', methods=['GET'])
@require_auth_api
def get_file_info():
    """获取文件信息（需要读取权限）"""
    try:
        file_path = request.args.get('path', '')
        if not file_path:
            return jsonify({
                'success': False,
                'message': '文件路径不能为空'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 获取文件信息: {file_path}")
        
        file_service = FileService()
        result = file_service.get_file_info(file_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/create_folder', methods=['POST'])
@require_auth_api
def create_folder():
    """创建文件夹（需要写入权限）"""
    try:
        data = request.get_json()
        if not data or 'path' not in data or 'name' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        base_path = data['path']
        folder_name = data['name']
        
        # 构建完整的目录路径
        if base_path == '' or base_path == '.':
            directory_path = folder_name
        else:
            directory_path = base_path + '/' + folder_name
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 创建文件夹: {directory_path}")
        
        file_service = FileService()
        result = file_service.create_directory(directory_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"创建文件夹失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/delete', methods=['DELETE'])
@require_auth_api
def delete_file():
    """删除文件或目录（需要删除权限）"""
    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        file_path = data['path']
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 删除文件/目录: {file_path}")
        
        file_service = FileService()
        result = file_service.delete_file(file_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"删除文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/rename', methods=['PUT'])
@require_auth_api
def rename_file():
    """重命名文件或目录（需要读取和写入权限）"""
    try:
        data = request.get_json()
        if not data or 'old_path' not in data or 'new_name' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        old_path = data['old_path']
        new_name = data['new_name']
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 重命名文件/目录: {old_path} -> {new_name}")
        
        file_service = FileService()
        result = file_service.rename_file(old_path, new_name, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"重命名文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/move', methods=['PUT'])
@require_auth_api
def move_file():
    """移动文件或目录（需要读取和写入权限）"""
    try:
        data = request.get_json()
        if not data or 'source_path' not in data or 'target_path' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        source_path = data['source_path']
        target_path = data['target_path']
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 移动文件/目录: {source_path} -> {target_path}")
        
        file_service = FileService()
        result = file_service.move_file(source_path, target_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"移动文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/copy', methods=['POST'])
@require_auth_api
def copy_file():
    """复制文件或目录（需要读取和写入权限）"""
    try:
        data = request.get_json()
        if not data or 'source_path' not in data or 'target_path' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        source_path = data['source_path']
        target_path = data['target_path']
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 复制文件/目录: {source_path} -> {target_path}")
        
        file_service = FileService()
        result = file_service.copy_file(source_path, target_path, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"复制文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/search', methods=['GET'])
@require_auth_api
def search_files():
    """搜索文件（需要读取权限）"""
    try:
        search_path = request.args.get('path', '.')
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'message': '搜索查询不能为空'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 搜索文件: {search_path}, 查询: {query}")
        
        file_service = FileService()
        result = file_service.search_files(search_path, query, user_ip, user_agent, current_user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"搜索文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
