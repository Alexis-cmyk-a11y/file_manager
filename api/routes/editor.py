"""
在线编辑器API路由
提供文件编辑、保存、搜索等功能
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter.util import get_remote_address

from services.editor_service import EditorService
from services.security_service import SecurityService

bp = Blueprint('editor', __name__, url_prefix='/api/editor')

@bp.route('/open', methods=['POST'])
def open_file():
    """打开文件进行编辑"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    file_path = data.get('path', '')
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    try:
        editor_service = EditorService()
        
        # 检查文件是否可以编辑
        if not editor_service.can_edit_file(file_path):
            return jsonify({'success': False, 'message': '该文件类型不支持编辑'}), 400
        
        # 读取文件内容
        result = editor_service.read_file_content(file_path)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"打开文件失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/save', methods=['POST'])
def save_file():
    """保存文件内容"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    file_path = data.get('path', '')
    content = data.get('content', '')
    
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    try:
        editor_service = EditorService()
        
        # 保存文件内容
        result = editor_service.save_file_content(file_path, content)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"保存文件失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/preview', methods=['GET'])
def preview_file():
    """获取文件预览"""
    file_path = request.args.get('path', '')
    max_lines = request.args.get('max_lines', 100, type=int)
    
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    try:
        editor_service = EditorService()
        result = editor_service.get_file_preview(file_path, max_lines)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"获取文件预览失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/search', methods=['POST'])
def search_in_file():
    """在文件中搜索文本"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    file_path = data.get('path', '')
    search_term = data.get('search_term', '')
    case_sensitive = data.get('case_sensitive', False)
    
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    if not search_term:
        return jsonify({'success': False, 'message': '搜索词不能为空'}), 400
    
    try:
        editor_service = EditorService()
        result = editor_service.search_in_file(file_path, search_term, case_sensitive)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"文件搜索失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/check-editability', methods=['GET'])
def check_editability():
    """检查文件是否可以编辑"""
    file_path = request.args.get('path', '')
    
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    try:
        editor_service = EditorService()
        can_edit = editor_service.can_edit_file(file_path)
        syntax_mode = editor_service.get_syntax_mode(file_path) if can_edit else None
        
        return jsonify({
            'success': True,
            'can_edit': can_edit,
            'syntax_mode': syntax_mode,
            'file_path': file_path
        })
        
    except Exception as e:
        current_app.logger.error(f"检查文件可编辑性失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/info', methods=['GET'])
def get_file_info():
    """获取文件编辑相关信息"""
    file_path = request.args.get('path', '')
    
    if not file_path:
        return jsonify({'success': False, 'message': '文件路径不能为空'}), 400
    
    try:
        editor_service = EditorService()
        
        # 检查文件是否可以编辑
        can_edit = editor_service.can_edit_file(file_path)
        
        if not can_edit:
            return jsonify({
                'success': True,
                'can_edit': False,
                'message': '该文件类型不支持编辑'
            })
        
        # 获取文件信息
        file_info = editor_service.read_file_content(file_path)
        
        if not file_info.get('success'):
            return jsonify(file_info)
        
        # 添加额外信息
        file_info.update({
            'syntax_mode': editor_service.get_syntax_mode(file_path),
            'can_edit': True
        })
        
        return jsonify(file_info)
        
    except Exception as e:
        current_app.logger.error(f"获取文件信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
