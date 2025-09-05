"""
文件下载API路由
处理文件下载相关的请求
"""

from flask import Blueprint, request, jsonify, current_app, send_file
from services.download_service import DownloadService
from utils.logger import get_logger
from utils.auth_middleware import require_auth_api, get_current_user
from utils.file_utils import FileUtils
import os


logger = get_logger(__name__)
bp = Blueprint('download', __name__, url_prefix='/api')

def get_user_info():
    """获取用户信息"""
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return user_ip, user_agent

@bp.route('/download', methods=['GET'])
@require_auth_api
def download_file():
    """智能下载文件或目录（需要读取权限）"""
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
        
        logger.info(f"用户 {current_user['email']} 下载文件/目录: {file_path}")
        
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
@require_auth_api
def download_directory_as_zip():
    """将目录打包为ZIP文件下载（需要读取权限）"""
    try:
        directory_path = request.args.get('path', '')
        if not directory_path:
            return jsonify({
                'success': False,
                'message': '目录路径不能为空'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 下载目录为ZIP: {directory_path}")
        
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
        logger.error(f"目录ZIP下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/download_web_file', methods=['POST'])
@require_auth_api
def download_web_file():
    """从公网下载文件到服务器的download目录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据不能为空'
            }), 400
        
        url = data.get('url', '').strip()
        filename = data.get('filename', '').strip()
        
        if not url:
            return jsonify({
                'success': False,
                'message': '下载URL不能为空'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 从网络下载文件: {url} -> {filename}")
        
        download_service = DownloadService()
        
        # 下载网络文件
        result = download_service.download_web_file(url, filename, user_ip, user_agent)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"网络文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/list_downloaded_files', methods=['GET'])
@require_auth_api
def list_downloaded_files():
    """列出download目录中的所有文件"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        
        logger.info(f"用户 {current_user['email']} 查看已下载文件列表")
        
        download_service = DownloadService()
        result = download_service.list_downloaded_files()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取下载文件列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/delete_downloaded_file', methods=['DELETE'])
@require_auth_api
def delete_downloaded_file():
    """删除download目录中的文件"""
    try:
        filename = request.args.get('filename', '')
        if not filename:
            return jsonify({
                'success': False,
                'message': '文件名不能为空'
            }), 400
        
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 删除已下载文件: {filename}")
        
        download_service = DownloadService()
        result = download_service.delete_downloaded_file(filename, user_ip, user_agent)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"删除下载文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/download/shared/<owner>/<path:filename>', methods=['GET'])
@require_auth_api
def download_shared_file(owner, filename):
    """下载共享文件"""
    try:
        # 获取当前用户信息
        current_user = get_current_user()
        user_ip, user_agent = get_user_info()
        
        logger.info(f"用户 {current_user['email']} 下载共享文件: {owner}/{filename}")
        
        # 构建共享文件路径
        shared_file_path = os.path.join('home', 'shared', f'{owner}_shared', filename)
        
        # 检查文件是否存在
        if not os.path.exists(shared_file_path):
            return jsonify({
                'success': False,
                'message': '文件不存在'
            }), 404
        
        # 检查是否为文件
        if not os.path.isfile(shared_file_path):
            return jsonify({
                'success': False,
                'message': '路径不是文件'
            }), 400
        
        # 获取文件信息
        file_info = FileUtils.get_file_info(shared_file_path)
        
        # 记录操作日志
        download_service = DownloadService()
        download_service._log_operation(
            operation_type='download_shared',
            file_path=shared_file_path,
            file_name=filename,
            file_size=file_info['size'],
            user_ip=user_ip,
            user_agent=user_agent,
            status='success'
        )
        
        # 发送文件
        return send_file(
            os.path.abspath(shared_file_path),
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"共享文件下载失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@bp.route('/stats', methods=['GET'])
@require_auth_api
def get_download_stats():
    """获取下载统计信息"""
    try:
        days = request.args.get('days', 7, type=int)
        
        # 获取当前用户信息
        current_user = get_current_user()
        
        logger.info(f"用户 {current_user['email']} 查看下载统计信息")
        
        download_service = DownloadService()
        result = download_service.get_download_stats(days)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取下载统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
