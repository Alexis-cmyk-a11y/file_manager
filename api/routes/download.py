"""
文件下载API路由
处理文件下载相关的请求
"""

from flask import Blueprint, request, jsonify, current_app
from services.download_service import DownloadService
from utils.logger import get_logger

logger = get_logger(__name__)
bp = Blueprint('download', __name__, url_prefix='/api')

def get_user_info():
    """获取用户信息"""
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return user_ip, user_agent

@bp.route('/download', methods=['GET'])
def download_file():
    """智能下载文件或目录"""
    try:
        file_path = request.args.get('path', '')
        if not file_path:
            return jsonify({
                'success': False,
                'message': '文件路径不能为空'
            }), 400
        
        user_ip, user_agent = get_user_info()
        
        download_service = DownloadService()
        
        # 验证下载路径
        validation = download_service.validate_download_path(file_path)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'message': validation['error']
            }), 400
        
        # 智能判断是文件还是目录
        import os
        if os.path.isfile(file_path):
            # 下载文件
            return download_service.download_file(file_path, user_ip, user_agent)
        elif os.path.isdir(file_path):
            # 下载目录为ZIP
            return download_service.download_directory_as_zip(file_path, user_ip, user_agent)
        else:
            return jsonify({
                'success': False,
                'message': '路径不存在'
            }), 404
        
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/download_zip', methods=['GET'])
def download_directory_as_zip():
    """将目录打包为ZIP文件下载"""
    try:
        directory_path = request.args.get('path', '')
        if not directory_path:
            return jsonify({
                'success': False,
                'message': '目录路径不能为空'
            }), 400
        
        user_ip, user_agent = get_user_info()
        
        download_service = DownloadService()
        
        # 验证下载路径
        validation = download_service.validate_download_path(directory_path)
        if not validation['valid']:
            return jsonify({
                'success': False,
                'message': validation['error']
            }), 400
        
        # 下载目录为ZIP
        return download_service.download_directory_as_zip(directory_path, user_ip, user_agent)
        
    except Exception as e:
        logger.error(f"目录下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
def get_download_stats():
    """获取下载统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        
        download_service = DownloadService()
        result = download_service.get_download_stats(days)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取下载统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
