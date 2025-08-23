"""
文件上传API路由
处理文件上传相关的请求
"""

from flask import Blueprint, request, jsonify, current_app

from services.upload_service import UploadService

bp = Blueprint('upload', __name__, url_prefix='/api')

@bp.route('/upload', methods=['POST'])
def upload_file():
    """上传文件到指定目录"""
    current_app.logger.info(f"收到上传请求")
    
    # 获取目标目录
    target_dir = request.form.get('path', '')
    
    # 检查是否有文件上传
    if 'files' not in request.files:
        current_app.logger.warning("上传请求中没有文件")
        return jsonify({'success': False, 'message': '没有文件被上传'}), 400
    
    uploaded_files = request.files.getlist('files')
    current_app.logger.info(f"获取到 {len(uploaded_files)} 个文件")
    
    if not uploaded_files:
        current_app.logger.warning("上传的文件列表为空")
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    try:
        upload_service = UploadService()
        result = upload_service.upload_files(uploaded_files, target_dir)
        
        # 添加缓存控制头
        response = jsonify(result)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
