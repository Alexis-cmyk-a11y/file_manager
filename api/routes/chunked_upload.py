"""
分块上传API路由
处理大文件的分块上传、断点续传相关请求
"""

from flask import Blueprint, request, jsonify, current_app
from services.chunked_upload_service import ChunkedUploadService
from utils.logger import get_logger
from utils.auth_middleware import require_auth_api, get_current_user

logger = get_logger(__name__)
bp = Blueprint('chunked_upload', __name__, url_prefix='/api')

@bp.route('/chunked/init', methods=['POST'])
@require_auth_api
def initialize_chunked_upload():
    """初始化分块上传"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        filename = data.get('filename')
        file_size = data.get('file_size')
        target_directory = data.get('target_directory', '.')
        client_chunk_size = data.get('chunk_size')  # 获取客户端发送的块大小
        
        if not filename or not file_size:
            return jsonify({
                'success': False,
                'message': '文件名和文件大小不能为空'
            }), 400
        
        if not isinstance(file_size, int) or file_size <= 0:
            return jsonify({
                'success': False,
                'message': '文件大小必须是正整数'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        logger.info(f"用户 {user_id} 初始化分块上传: {filename} ({file_size} bytes)")
        
        chunked_service = ChunkedUploadService()
        result = chunked_service.initialize_upload(
            filename=filename,
            file_size=file_size,
            user_id=user_id,
            target_directory=target_directory,
            chunk_size=client_chunk_size,  # 传递客户端块大小
            current_user=current_user
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"初始化分块上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/chunked/upload/<upload_id>/<int:chunk_index>', methods=['POST'])
@require_auth_api
def upload_chunk(upload_id, chunk_index):
    """上传文件块"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        # 获取块数据
        if 'chunk' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有找到块数据'
            }), 400
        
        chunk_file = request.files['chunk']
        chunk_data = chunk_file.read()
        
        if not chunk_data:
            return jsonify({
                'success': False,
                'message': '块数据为空'
            }), 400
        
        # 获取块哈希（可选）
        chunk_hash = request.form.get('chunk_hash')
        
        logger.info(f"用户 {user_id} 上传块: {upload_id}[{chunk_index}] ({len(chunk_data)} bytes)")
        
        chunked_service = ChunkedUploadService()
        result = chunked_service.upload_chunk(
            upload_id=upload_id,
            chunk_index=chunk_index,
            chunk_data=chunk_data,
            chunk_hash=chunk_hash
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"上传块失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/chunked/status/<upload_id>', methods=['GET'])
@require_auth_api
def get_upload_status(upload_id):
    """获取上传状态"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        chunked_service = ChunkedUploadService()
        result = chunked_service.get_upload_status(upload_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取上传状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/chunked/cancel/<upload_id>', methods=['POST'])
@require_auth_api
def cancel_upload(upload_id):
    """取消上传"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        logger.info(f"用户 {user_id} 取消上传: {upload_id}")
        
        chunked_service = ChunkedUploadService()
        result = chunked_service.cancel_upload(upload_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"取消上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/chunked/list', methods=['GET'])
@require_auth_api
def get_upload_list():
    """获取上传列表"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        chunked_service = ChunkedUploadService()
        result = chunked_service.get_upload_list(user_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取上传列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/chunked/merge/<upload_id>', methods=['POST'])
@require_auth_api
def merge_file(upload_id):
    """手动触发文件合并"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_id = current_user.get('email', 'anonymous')
        
        logger.info(f"用户 {user_id} 手动触发文件合并: {upload_id}")
        
        chunked_service = ChunkedUploadService()
        result = chunked_service._merge_file(upload_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"合并文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

