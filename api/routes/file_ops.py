"""
文件操作API路由
包含文件列表、复制、移动、删除、重命名、创建文件夹等操作
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter.util import get_remote_address

from services.file_service import FileService
from services.security_service import SecurityService

bp = Blueprint('file_ops', __name__, url_prefix='/api')

@bp.route('/list', methods=['GET'])
def list_files():
    """列出指定目录下的所有文件和子目录"""
    rel_path = request.args.get('path', '')
    
    try:
        file_service = FileService()
        result = file_service.list_directory(rel_path)
        
        # 添加缓存控制头，确保每次请求都返回最新数据
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"列出目录内容失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/copy', methods=['POST'])
def copy_item():
    """复制文件或目录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    try:
        file_service = FileService()
        result = file_service.copy_item(source_path, target_dir)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"复制失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/move', methods=['POST'])
def move_item():
    """移动文件或目录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    try:
        file_service = FileService()
        result = file_service.move_item(source_path, target_dir)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"移动失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/delete', methods=['POST'])
def delete_item():
    """删除文件或目录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    path = data.get('path', '')
    
    try:
        file_service = FileService()
        result = file_service.delete_item(path)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"删除失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/create_folder', methods=['POST'])
def create_folder():
    """创建新文件夹"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    parent_dir = data.get('path', '')
    folder_name = data.get('name', '')
    
    try:
        file_service = FileService()
        result = file_service.create_folder(parent_dir, folder_name)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"创建文件夹失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/rename', methods=['POST'])
def rename_item():
    """重命名文件或目录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    path = data.get('path', '')
    new_name = data.get('new_name', '')
    
    try:
        file_service = FileService()
        result = file_service.rename_item(path, new_name)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"重命名失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
