import os
import sys
import shutil
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import os
import sys
import importlib.util
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='file_manager.log'
)
logger = logging.getLogger(__name__)

def load_config_from_file(config_path):
    """从指定路径加载config.py文件"""
    try:
        spec = importlib.util.spec_from_file_location("external_config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module.Config
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return None

def get_config():
    # 获取当前可执行文件所在目录
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试从外部导入config.py
    config_path = os.path.join(base_dir, 'config.py')
    logger.info(f"尝试加载配置文件: {config_path}")
    
    if os.path.exists(config_path):
        config = load_config_from_file(config_path)
        if config:
            logger.info("成功加载外部配置文件")
            return config
    
    # 提供默认配置
    logger.warning("使用默认配置")
    class DefaultConfig:
        FILE_OPERATION_PERMISSION = 'read_write'
        SERVER_HOST = '0.0.0.0'
        SERVER_PORT = 5000
        LOG_FILE = 'file_manager.log'
        LOG_LEVEL = 'INFO'
    return DefaultConfig

Config = get_config()

# 初始化Flask应用
app = Flask(__name__)

# 处理打包后的资源路径
def resource_path(relative_path):
    """获取打包后资源的绝对路径"""
    try:
        # PyInstaller创建的临时文件夹中的路径
        base_path = sys._MEIPASS
    except Exception:
        # 正常开发环境路径
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# 从配置文件加载配置
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# 设置根目录
ROOT_DIR = Config.ROOT_DIR

# 确保静态文件和模板路径正确
app.static_folder = resource_path('static')
app.template_folder = resource_path('templates')

# 配置日志
def setup_logger():
    log_level = getattr(logging, Config.LOG_LEVEL)
    log_formatter = logging.Formatter(Config.LOG_FORMAT)
    
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        Config.LOG_FILE, 
        maxBytes=Config.LOG_MAX_SIZE, 
        backupCount=Config.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(log_formatter)
    
    # 配置应用日志
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    app.logger.addHandler(console_handler)
    
    return app.logger

# 初始化日志
logger = setup_logger()
logger.info("应用启动，根目录设置为: %s", ROOT_DIR)

@app.route('/')
def index():
    """渲染主页"""
    app.logger.info("访问主页")
    return render_template('index.html', app_name=Config.APP_NAME)

@app.route('/api/list', methods=['GET'])
def list_files():
    """列出指定目录下的所有文件和子目录"""
    # 获取相对路径参数，默认为根目录
    rel_path = request.args.get('path', '')
    
    # 构建完整路径
    full_path = os.path.join(ROOT_DIR, rel_path)
    
    logger.info(f"列出目录内容: {full_path}")
    
    # 检查路径是否存在且在根目录下
    if not os.path.exists(full_path):
        logger.warning(f"请求的路径不存在: {full_path}")
        return jsonify({'success': False, 'message': '路径不存在'}), 404
    
    if not full_path.startswith(ROOT_DIR):
        logger.warning(f"尝试访问根目录之外的路径: {full_path}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    try:
        # 获取目录内容
        items = []
        for item in os.listdir(full_path):
            try:
                item_path = os.path.join(full_path, item)
                item_type = 'directory' if os.path.isdir(item_path) else 'file'
                item_size = os.path.getsize(item_path) if item_type == 'file' else 0
                items.append({
                    'name': item,
                    'type': item_type,
                    'size': item_size,
                    'path': os.path.join(rel_path, item).replace('\\', '/'),
                    'modified': os.path.getmtime(item_path)
                })
            except Exception as item_error:
                logger.error(f"获取文件信息失败: {item}, 错误: {str(item_error)}")
        
        # 按类型和名称排序：先目录后文件，同类型按名称排序
        items.sort(key=lambda x: (0 if x['type'] == 'directory' else 1, x['name'].lower()))
        
        logger.debug(f"目录 {full_path} 中找到 {len(items)} 个项目")
        return jsonify({
            'success': True,
            'path': rel_path,
            'items': items,
            'current_dir': full_path
        })
    except Exception as e:
        logger.error(f"列出目录内容失败: {full_path}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件到指定目录"""
    # 检查是否启用上传功能
    if not Config.ENABLE_UPLOAD:
        logger.warning("尝试上传文件，但上传功能已禁用")
        return jsonify({'success': False, 'message': '上传功能已禁用'}), 403
    
    # 获取目标目录
    target_dir = request.form.get('path', '')
    full_target_dir = os.path.join(ROOT_DIR, target_dir)
    
    logger.info(f"尝试上传文件到目录: {full_target_dir}")
    
    # 检查目标目录是否存在且在根目录下
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"上传目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
    if not full_target_dir.startswith(ROOT_DIR):
        logger.warning(f"尝试上传到根目录之外的路径: {full_target_dir}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    # 检查是否有文件上传
    if 'files' not in request.files:
        logger.warning("上传请求中没有文件")
        return jsonify({'success': False, 'message': '没有文件被上传'}), 400
    
    uploaded_files = request.files.getlist('files')
    
    if not uploaded_files:
        logger.warning("上传的文件列表为空")
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    try:
        uploaded_count = 0
        uploaded_info = []
        
        for file in uploaded_files:
            # 检查文件名是否为空
            if file.filename == '':
                continue
            
            # 检查文件类型是否允许
            if Config.ALLOWED_EXTENSIONS and not any(file.filename.lower().endswith(ext) for ext in Config.ALLOWED_EXTENSIONS):
                logger.warning(f"不允许的文件类型: {file.filename}")
                continue
            
            # 保存文件
            filename = secure_filename(file.filename)
            file_path = os.path.join(full_target_dir, filename)
            file.save(file_path)
            
            file_size = os.path.getsize(file_path)
            logger.info(f"文件上传成功: {filename}, 大小: {file_size} 字节")
            
            uploaded_count += 1
            uploaded_info.append({
                'name': filename,
                'path': os.path.join(target_dir, filename).replace('\\', '/'),
                'size': file_size
            })
        
        if uploaded_count == 0:
            return jsonify({'success': False, 'message': '没有文件被成功上传'}), 400
        
        return jsonify({
            'success': True,
            'message': f'成功上传 {uploaded_count} 个文件',
            'files': uploaded_info
        })
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    """下载指定文件"""
    # 检查是否启用下载功能
    if not Config.ENABLE_DOWNLOAD:
        logger.warning("尝试下载文件，但下载功能已禁用")
        return jsonify({'success': False, 'message': '下载功能已禁用'}), 403
    
    # 获取文件路径
    file_path = request.args.get('path', '')
    full_path = os.path.join(ROOT_DIR, file_path)
    
    logger.info(f"尝试下载文件: {full_path}")
    
    # 检查文件是否存在且在根目录下
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        logger.warning(f"请求下载的文件不存在: {full_path}")
        return jsonify({'success': False, 'message': '文件不存在'}), 404
    
    if not full_path.startswith(ROOT_DIR):
        logger.warning(f"尝试下载根目录之外的文件: {full_path}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的文件'}), 403
    
    try:
        # 获取文件所在目录和文件名
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        
        logger.info(f"下载文件: {filename}, 大小: {os.path.getsize(full_path)} 字节")
        
        # 发送文件
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/copy', methods=['POST'])
def copy_item():
    """复制文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试复制文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    logger.info(f"尝试复制: {source_path} 到 {target_dir}")
    
    # 构建完整路径
    full_source_path = os.path.join(ROOT_DIR, source_path)
    full_target_dir = os.path.join(ROOT_DIR, target_dir)
    
    # 检查源路径和目标目录是否存在且在根目录下
    if not os.path.exists(full_source_path):
        logger.warning(f"源文件或目录不存在: {full_source_path}")
        return jsonify({'success': False, 'message': '源文件或目录不存在'}), 404
    
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
    if not full_source_path.startswith(ROOT_DIR) or not full_target_dir.startswith(ROOT_DIR):
        logger.warning(f"尝试访问根目录之外的路径: 源={full_source_path}, 目标={full_target_dir}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    try:
        # 获取源文件/目录名
        source_name = os.path.basename(full_source_path)
        target_path = os.path.join(full_target_dir, source_name)
        
        # 检查目标路径是否已存在
        if os.path.exists(target_path):
            logger.warning(f"目标路径已存在同名文件或目录: {target_path}")
            return jsonify({'success': False, 'message': f'目标路径已存在同名文件或目录: {source_name}'}), 409
        
        # 复制文件或目录
        is_file = os.path.isfile(full_source_path)
        if is_file:
            shutil.copy2(full_source_path, target_path)
            logger.info(f"文件复制成功: {full_source_path} -> {target_path}")
        else:
            shutil.copytree(full_source_path, target_path)
            logger.info(f"目录复制成功: {full_source_path} -> {target_path}")
        
        return jsonify({
            'success': True,
            'message': f'{"文件" if is_file else "目录"} {source_name} 复制成功'
        })
    except Exception as e:
        logger.error(f"复制失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/move', methods=['POST'])
def move_item():
    """移动文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试移动文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    logger.info(f"尝试移动: {source_path} 到 {target_dir}")
    
    # 构建完整路径
    full_source_path = os.path.join(ROOT_DIR, source_path)
    full_target_dir = os.path.join(ROOT_DIR, target_dir)
    
    # 检查源路径和目标目录是否存在且在根目录下
    if not os.path.exists(full_source_path):
        logger.warning(f"源文件或目录不存在: {full_source_path}")
        return jsonify({'success': False, 'message': '源文件或目录不存在'}), 404
    
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
    if not full_source_path.startswith(ROOT_DIR) or not full_target_dir.startswith(ROOT_DIR):
        logger.warning(f"尝试访问根目录之外的路径: 源={full_source_path}, 目标={full_target_dir}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    try:
        # 获取源文件/目录名
        source_name = os.path.basename(full_source_path)
        target_path = os.path.join(full_target_dir, source_name)
        
        # 检查目标路径是否已存在
        if os.path.exists(target_path):
            logger.warning(f"目标路径已存在同名文件或目录: {target_path}")
            return jsonify({'success': False, 'message': f'目标路径已存在同名文件或目录: {source_name}'}), 409
        
        # 移动文件或目录
        is_file = os.path.isfile(full_source_path)
        shutil.move(full_source_path, target_path)
        logger.info(f"{'文件' if is_file else '目录'}移动成功: {full_source_path} -> {target_path}")
        
        return jsonify({
            'success': True,
            'message': f'{"文件" if is_file else "目录"} {source_name} 移动成功'
        })
    except Exception as e:
        logger.error(f"移动失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_item():
    """删除文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试删除文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    path = data.get('path', '')
    
    logger.info(f"尝试删除: {path}")
    
    # 构建完整路径
    full_path = os.path.join(ROOT_DIR, path)
    
    # 检查路径是否存在且在根目录下
    if not os.path.exists(full_path):
        logger.warning(f"要删除的文件或目录不存在: {full_path}")
        return jsonify({'success': False, 'message': '文件或目录不存在'}), 404
    
    if not full_path.startswith(ROOT_DIR):
        logger.warning(f"尝试删除根目录之外的路径: {full_path}")
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    try:
        # 删除文件或目录
        item_name = os.path.basename(full_path)
        is_file = os.path.isfile(full_path)
        if is_file:
            os.remove(full_path)
            item_type = '文件'
            logger.info(f"文件删除成功: {full_path}")
        else:
            shutil.rmtree(full_path)
            item_type = '目录'
            logger.info(f"目录删除成功: {full_path}")
        
        return jsonify({
            'success': True,
            'message': f'{item_type} {item_name} 删除成功'
        })
    except Exception as e:
        logger.error(f"删除失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/create_folder', methods=['POST'])
def create_folder():
    """创建新文件夹"""
    data = request.get_json()
    parent_dir = data.get('path', '')
    folder_name = data.get('name', '')
    
    # 检查文件夹名是否有效
    if not folder_name or folder_name.strip() == '':
        return jsonify({'success': False, 'message': '文件夹名不能为空'}), 400
    
    # 构建完整路径
    full_parent_dir = os.path.join(ROOT_DIR, parent_dir)
    full_path = os.path.join(full_parent_dir, folder_name)
    
    # 检查父目录是否存在且在根目录下
    if not os.path.exists(full_parent_dir) or not os.path.isdir(full_parent_dir):
        return jsonify({'success': False, 'message': '父目录不存在'}), 404
    
    if not full_parent_dir.startswith(ROOT_DIR):
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    # 检查文件夹是否已存在
    if os.path.exists(full_path):
        return jsonify({'success': False, 'message': f'文件夹 {folder_name} 已存在'}), 409
    
    try:
        # 创建文件夹
        os.makedirs(full_path)
        
        return jsonify({
            'success': True,
            'message': f'文件夹 {folder_name} 创建成功',
            'folder': {
                'name': folder_name,
                'path': os.path.join(parent_dir, folder_name).replace('\\', '/'),
                'type': 'directory'
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/rename', methods=['POST'])
def rename_item():
    """重命名文件或目录"""
    data = request.get_json()
    path = data.get('path', '')
    new_name = data.get('new_name', '')
    
    # 检查新名称是否有效
    if not new_name or new_name.strip() == '':
        return jsonify({'success': False, 'message': '新名称不能为空'}), 400
    
    # 构建完整路径
    full_path = os.path.join(ROOT_DIR, path)
    
    # 检查路径是否存在且在根目录下
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'message': '文件或目录不存在'}), 404
    
    if not full_path.startswith(ROOT_DIR):
        return jsonify({'success': False, 'message': '无法访问根目录之外的路径'}), 403
    
    try:
        # 获取父目录和新路径
        parent_dir = os.path.dirname(full_path)
        new_path = os.path.join(parent_dir, new_name)
        
        # 检查新路径是否已存在
        if os.path.exists(new_path):
            return jsonify({'success': False, 'message': f'已存在同名文件或目录: {new_name}'}), 409
        
        # 重命名文件或目录
        os.rename(full_path, new_path)
        
        # 计算相对路径
        rel_parent_dir = os.path.dirname(path)
        rel_new_path = os.path.join(rel_parent_dir, new_name).replace('\\', '/')
        
        return jsonify({
            'success': True,
            'message': f'{"文件" if os.path.isfile(new_path) else "目录"} 重命名成功',
            'new_path': rel_new_path,
            'new_name': new_name
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG_MODE, host=Config.SERVER_HOST, port=Config.SERVER_PORT)