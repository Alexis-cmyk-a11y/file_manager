"""
系统信息API路由
提供系统状态、配置信息等接口
"""

from flask import Blueprint, request, jsonify, current_app, render_template

from services.system_service import SystemService

bp = Blueprint('system', __name__)

@bp.route('/', methods=['GET'])
def index():
    """渲染主页"""
    current_app.logger.info("访问主页")
    return render_template('index.html', app_name=current_app.config.get('APP_NAME', '文件管理系统'))

@bp.route('/api/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        system_service = SystemService()
        result = system_service.get_system_info()
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f"获取系统信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
