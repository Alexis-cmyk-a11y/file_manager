"""
文件下载API路由
处理文件下载相关的请求
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory

from services.download_service import DownloadService

bp = Blueprint('download', __name__, url_prefix='/api')

@bp.route('/download', methods=['GET'])
def download_file():
    """下载指定文件"""
    # 获取文件路径
    file_path = request.args.get('path', '')
    
    try:
        download_service = DownloadService()
        result = download_service.download_file(file_path)
        
        if result['success']:
            directory = result['directory']
            filename = result['filename']
            return send_from_directory(directory, filename, as_attachment=True)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        current_app.logger.error(f"文件下载失败: {str(e)}")
        return jsonify({'success': False, 'message': '文件下载失败，请稍后重试'}), 500
