"""
文件上传API路由
处理文件上传相关的请求
"""

from flask import Blueprint, request, jsonify, current_app
from services.upload_service import UploadService
from utils.logger import get_logger
from utils.auth_middleware import require_auth_api, get_current_user

logger = get_logger(__name__)
bp = Blueprint('upload', __name__, url_prefix='/api')

def get_user_info():
    """获取用户信息"""
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return user_ip, user_agent

@bp.route('/upload', methods=['POST'])
@require_auth_api
def upload_file():
    """上传单个文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        target_directory = request.form.get('target_directory', '.')
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 上传文件: {file.filename} 到 {target_directory}")
        
        upload_service = UploadService()
        
        # 验证文件
        validation = upload_service.validate_upload(file)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'message': validation['error']
            }), 400
        
        # 上传文件
        result = upload_service.upload_file(file, target_directory, user_ip, user_agent)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/upload_multiple', methods=['POST'])
@require_auth_api
def upload_multiple_files():
    """上传多个文件"""
    try:
        if 'files' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        target_directory = request.form.get('target_directory', '.')
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 批量上传 {len(files)} 个文件到 {target_directory}")
        
        upload_service = UploadService()
        
        # 验证所有文件
        valid_files = []
        for file in files:
            validation = upload_service.validate_upload(file)
            if validation['valid']:
                valid_files.append(file)
            else:
                logger.warning(f"文件验证失败: {file.filename} - {validation['error']}")
        
        if not valid_files:
            return jsonify({
                'success': False,
                'message': '没有有效的文件可以上传'
            }), 400
        
        # 上传文件
        result = upload_service.upload_multiple_files(valid_files, target_directory, user_ip, user_agent)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"批量文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_upload_stats():
    """获取上传统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        
        upload_service = UploadService()
        result = upload_service.get_upload_stats(days)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取上传统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
