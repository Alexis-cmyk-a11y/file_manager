import os
import sys
import shutil
import logging
import hashlib
import mimetypes
from datetime import datetime
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, abort, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import importlib.util

def setup_logging():
    """配置日志记录，支持日志文件轮转"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # 日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 控制台日志
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件日志（轮转）
    file_handler = RotatingFileHandler(
        'file_manager.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'  # 增加编码设置，避免日志文件乱码
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

def load_config_from_file(config_path):
    """从指定路径加载config.py文件"""
    try:
        spec = importlib.util.spec_from_file_location("external_config", config_path)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        return config_module.Config
    except ImportError as e:
        logger.error(f"加载配置文件失败: 模块导入错误 - {str(e)}")
    except AttributeError as e:
        logger.error(f"加载配置文件失败: 配置类未定义 - {str(e)}")
    except Exception as e:
        logger.error(f"加载配置文件失败: 未知错误 - {str(e)}")
    return None

def get_config():
    """获取配置，支持环境变量覆盖"""
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
        def __init__(self):
            self.FILE_OPERATION_PERMISSION = os.getenv('FILE_OPERATION_PERMISSION', 'read_write')
            self.SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
            self.SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
            self.LOG_FILE = os.getenv('LOG_FILE', 'file_manager.log')
            self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
            self.LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
            self.LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
            self.ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.abspath(__file__)))
            self.MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 50 * 1024 * 1024 * 1024))
            self.ENABLE_DOWNLOAD = os.getenv('ENABLE_DOWNLOAD', 'true').lower() == 'true'
            self.ENABLE_DELETE = os.getenv('ENABLE_DELETE', 'true').lower() == 'true'
            self.ENABLE_UPLOAD = os.getenv('ENABLE_UPLOAD', 'true').lower() == 'true'
            self.ENABLE_FILE_OPS = os.getenv('ENABLE_FILE_OPS', 'true').lower() == 'true'
            self.ENV = os.getenv('ENV', 'production')
            self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            self.APP_NAME = os.getenv('APP_NAME', '文件管理系统')
            self.SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
            self.ALLOWED_EXTENSIONS = set()
            self.FORBIDDEN_EXTENSIONS = {'.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar'}
            self.MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 100 * 1024 * 1024))
    
    return DefaultConfig()

Config = get_config()

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# 启用CORS
CORS(app)

# 初始化速率限制器
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT] if hasattr(Config, 'RATE_LIMIT') else ["100 per minute"]
)

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

# 设置根目录 - 优先使用配置文件中的设置
if hasattr(Config, 'ROOT_DIR') and Config.ROOT_DIR != '/path/to/your/files':
    ROOT_DIR = Config.ROOT_DIR
else:
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

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

# 安全验证函数
def validate_path_safety(path):
    """验证路径安全性"""
    # 空路径表示根目录，这是允许的
    if not path:
        return True, ROOT_DIR
    
    # 检查路径遍历攻击
    if '..' in path or path.startswith('/') or ':' in path:
        return False, "无效的路径"
    
    # 构建完整路径
    full_path = os.path.join(ROOT_DIR, path)
    
    # 检查是否在根目录范围内
    if not os.path.abspath(full_path).startswith(os.path.abspath(ROOT_DIR)):
        return False, "无法访问根目录之外的路径"
    
    return True, full_path

def validate_file_extension(filename):
    """验证文件扩展名"""
    if not filename:
        return False, "文件名不能为空"
    
    # 检查禁止的文件类型
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext in Config.FORBIDDEN_EXTENSIONS:
        return False, f"不允许上传 {file_ext} 类型的文件"
    
    # 检查允许的文件类型（如果配置了的话）
    if hasattr(Config, 'ALLOWED_EXTENSIONS') and Config.ALLOWED_EXTENSIONS:
        if file_ext not in Config.ALLOWED_EXTENSIONS:
            return False, f"只允许上传 {', '.join(Config.ALLOWED_EXTENSIONS)} 类型的文件"
    
    return True, "文件类型验证通过"

def get_file_info(file_path):
    """获取文件信息"""
    try:
        stat = os.stat(file_path)
        file_info = {
            'name': os.path.basename(file_path),
            'type': 'directory' if os.path.isdir(file_path) else 'file',
            'size': stat.st_size if os.path.isfile(file_path) else 0,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'permissions': oct(stat.st_mode)[-3:],
            'mime_type': mimetypes.guess_type(file_path)[0] if os.path.isfile(file_path) else None
        }
        
        # 计算文件哈希（仅对文件）
        if os.path.isfile(file_path) and stat.st_size < 10 * 1024 * 1024:  # 小于10MB的文件
            try:
                with open(file_path, 'rb') as f:
                    file_info['md5'] = hashlib.md5(f.read()).hexdigest()
            except:
                file_info['md5'] = None
        
        return file_info
    except Exception as e:
        logger.error(f"获取文件信息失败: {file_path}, 错误: {str(e)}")
        return None

@app.route('/')
def index():
    """渲染主页"""
    app.logger.info("访问主页")
    return render_template('index.html', app_name=Config.APP_NAME)

@app.route('/api/list', methods=['GET'])
@limiter.limit("60 per minute")
def list_files():
    """列出指定目录下的所有文件和子目录"""
    # 获取相对路径参数，默认为根目录
    rel_path = request.args.get('path', '')
    
    # 验证路径安全性
    is_safe, result = validate_path_safety(rel_path)
    if not is_safe:
        logger.warning(f"路径安全检查失败: {rel_path}")
        return jsonify({'success': False, 'message': result}), 400
    
    full_path = result
    logger.info(f"列出目录内容: {full_path}")
    
    # 检查路径是否存在
    if not os.path.exists(full_path):
        logger.warning(f"请求的路径不存在: {full_path}")
        return jsonify({'success': False, 'message': '路径不存在'}), 404
    
    if not os.path.isdir(full_path):
        logger.warning(f"请求的路径不是目录: {full_path}")
        return jsonify({'success': False, 'message': '请求的路径不是目录'}), 400

    def get_directory_items(directory_path, relative_path):
        """获取目录内容并返回格式化列表"""
        items = []
        try:
            for item in os.listdir(directory_path):
                try:
                    item_path = os.path.join(directory_path, item)
                    file_info = get_file_info(item_path)
                    if file_info:
                        file_info['path'] = os.path.join(relative_path, item).replace('\\', '/')
                        items.append(file_info)
                except Exception as item_error:
                    logger.error(f"获取文件信息失败: {item}, 错误: {str(item_error)}")
            
            # 按类型和名称排序：先目录后文件，同类型按名称排序
            items.sort(key=lambda x: (0 if x['type'] == 'directory' else 1, x['name'].lower()))
            return items
        except PermissionError:
            logger.error(f"没有权限访问目录: {directory_path}")
            return []
        except Exception as e:
            logger.error(f"读取目录失败: {directory_path}, 错误: {str(e)}")
            return []

    try:
        items = get_directory_items(full_path, rel_path)
        
        # 计算目录统计信息
        total_files = len([item for item in items if item['type'] == 'file'])
        total_dirs = len([item for item in items if item['type'] == 'directory'])
        total_size = sum(item['size'] for item in items if item['type'] == 'file')
        
        logger.debug(f"目录 {full_path} 中找到 {len(items)} 个项目")
        return jsonify({
            'success': True,
            'path': rel_path,
            'items': items,
            'current_dir': full_path,
            'stats': {
                'total_items': len(items),
                'total_files': total_files,
                'total_directories': total_dirs,
                'total_size': total_size
            }
        })
    except Exception as e:
        logger.error(f"列出目录内容失败: {full_path}, 错误: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_file():
    """上传文件到指定目录"""
    logger.info(f"收到上传请求，配置: ENABLE_UPLOAD={Config.ENABLE_UPLOAD}")
    
    # 检查是否启用上传功能
    if not Config.ENABLE_UPLOAD:
        logger.warning("尝试上传文件，但上传功能已禁用")
        return jsonify({'success': False, 'message': '上传功能已禁用'}), 403
    
    # 获取目标目录
    target_dir = request.form.get('path', '')
    
    # 验证路径安全性
    is_safe, result = validate_path_safety(target_dir)
    if not is_safe:
        logger.warning(f"上传目标路径安全检查失败: {target_dir}")
        return jsonify({'success': False, 'message': result}), 400
    
    full_target_dir = result
    logger.info(f"尝试上传文件到目录: {full_target_dir}")
    
    # 检查目标目录是否存在
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"上传目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
    # 检查是否有文件上传
    logger.info(f"请求文件字段: {list(request.files.keys())}")
    if 'files' not in request.files:
        logger.warning("上传请求中没有文件")
        return jsonify({'success': False, 'message': '没有文件被上传'}), 400
    
    uploaded_files = request.files.getlist('files')
    logger.info(f"获取到 {len(uploaded_files)} 个文件")
    
    if not uploaded_files:
        logger.warning("上传的文件列表为空")
        return jsonify({'success': False, 'message': '没有选择文件'}), 400
    
    def save_uploaded_files(files, target_directory):
        """保存上传的文件并返回上传结果"""
        uploaded_count = 0
        uploaded_info = []
        errors = []
        
        for file in files:
            logger.info(f"处理文件: {file.filename}")
            if file.filename == '':
                logger.warning("跳过空文件名")
                continue
            
            # 验证文件扩展名
            logger.info(f"验证文件扩展名: {file.filename}")
            is_valid, message = validate_file_extension(file.filename)
            if not is_valid:
                logger.warning(f"文件扩展名验证失败: {file.filename} - {message}")
                errors.append(f"{file.filename}: {message}")
                continue
            
            # 验证文件大小
            if hasattr(Config, 'MAX_FILE_SIZE'):
                # 获取文件大小，兼容不同的Flask版本
                file_size = getattr(file, 'content_length', None)
                if file_size is None:
                    # 如果没有content_length，尝试从文件流获取
                    try:
                        file.seek(0, 2)  # 移动到文件末尾
                        file_size = file.tell()
                        file.seek(0)  # 重置到文件开头
                    except:
                        file_size = 0
                
                if file_size and file_size > Config.MAX_FILE_SIZE:
                    errors.append(f"{file.filename}: 文件大小超过限制 ({file_size} > {Config.MAX_FILE_SIZE})")
                    continue
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(target_directory, filename)
            
            # 检查文件是否已存在，如果存在则重命名
            counter = 1
            original_filename = filename
            while os.path.exists(file_path):
                name, ext = os.path.splitext(original_filename)
                filename = f"{name}_{counter}{ext}"
                file_path = os.path.join(target_directory, filename)
                counter += 1
            
            try:
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                logger.info(f"文件上传成功: {filename}, 大小: {file_size} 字节")
                
                uploaded_count += 1
                uploaded_info.append({
                    'name': filename,
                    'path': os.path.relpath(file_path, start=ROOT_DIR).replace('\\', '/'),
                    'size': file_size,
                    'md5': hashlib.md5(open(file_path, 'rb').read()).hexdigest()
                })
            except Exception as e:
                errors.append(f"{file.filename}: 保存失败 - {str(e)}")
                logger.error(f"文件保存失败: {file.filename}, 错误: {str(e)}")
        
        return uploaded_count, uploaded_info, errors

    try:
        uploaded_count, uploaded_info, errors = save_uploaded_files(uploaded_files, full_target_dir)
        
        response_data = {
            'success': uploaded_count > 0,
            'message': f'成功上传 {uploaded_count} 个文件',
            'files': uploaded_info,
            'total_uploaded': uploaded_count
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['message'] += f'，{len(errors)} 个文件上传失败'
        
        if uploaded_count == 0:
            return jsonify(response_data), 400
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/download', methods=['GET'])
@limiter.limit("30 per minute")
def download_file():
    """下载指定文件"""
    # 检查是否启用下载功能
    if not Config.ENABLE_DOWNLOAD:
        logger.warning("尝试下载文件，但下载功能已禁用")
        return jsonify({'success': False, 'message': '下载功能已禁用'}), 403
    
    # 获取文件路径
    file_path = request.args.get('path', '')
    
    # 验证路径安全性
    is_safe, result = validate_path_safety(file_path)
    if not is_safe:
        logger.warning(f"下载文件路径安全检查失败: {file_path}")
        return jsonify({'success': False, 'message': result}), 400
    
    full_path = result
    logger.info(f"尝试下载文件: {full_path}")
    
    # 检查文件是否存在
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        logger.warning(f"请求下载的文件不存在: {full_path}")
        return jsonify({'success': False, 'message': '文件不存在'}), 404

    def download_single_file(file_path):
        """下载单个文件"""
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        logger.info(f"下载文件: {filename}, 大小: {file_size} 字节")
        return send_from_directory(directory, filename, as_attachment=True)

    try:
        return download_single_file(full_path)
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': '文件下载失败，请稍后重试'}), 500

@app.route('/api/copy', methods=['POST'])
@limiter.limit("20 per minute")
def copy_item():
    """复制文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试复制文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    # 验证源路径安全性
    is_safe_source, source_result = validate_path_safety(source_path)
    if not is_safe_source:
        return jsonify({'success': False, 'message': source_result}), 400
    
    # 验证目标路径安全性
    is_safe_target, target_result = validate_path_safety(target_dir)
    if not is_safe_target:
        return jsonify({'success': False, 'message': target_result}), 400
    
    full_source_path = source_result
    full_target_dir = target_result
    
    logger.info(f"尝试复制: {full_source_path} 到 {full_target_dir}")
    
    # 检查源路径是否存在
    if not os.path.exists(full_source_path):
        logger.warning(f"源文件或目录不存在: {full_source_path}")
        return jsonify({'success': False, 'message': '源文件或目录不存在'}), 404
    
    # 检查目标目录是否存在
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
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
@limiter.limit("20 per minute")
def move_item():
    """移动文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试移动文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    source_path = data.get('source', '')
    target_dir = data.get('target', '')
    
    # 验证路径安全性
    is_safe_source, source_result = validate_path_safety(source_path)
    if not is_safe_source:
        return jsonify({'success': False, 'message': source_result}), 400
    
    is_safe_target, target_result = validate_path_safety(target_dir)
    if not is_safe_target:
        return jsonify({'success': False, 'message': target_result}), 400
    
    full_source_path = source_result
    full_target_dir = target_result
    
    logger.info(f"尝试移动: {full_source_path} 到 {full_target_dir}")
    
    # 检查源路径和目标目录是否存在
    if not os.path.exists(full_source_path):
        logger.warning(f"源文件或目录不存在: {full_source_path}")
        return jsonify({'success': False, 'message': '源文件或目录不存在'}), 404
    
    if not os.path.exists(full_target_dir) or not os.path.isdir(full_target_dir):
        logger.warning(f"目标目录不存在: {full_target_dir}")
        return jsonify({'success': False, 'message': '目标目录不存在'}), 404
    
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
        logger.error(f"移动失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': '移动操作失败，请稍后重试'}), 500

@app.route('/api/delete', methods=['POST'])
@limiter.limit("10 per minute")
def delete_item():
    """删除文件或目录"""
    # 检查是否启用文件操作功能
    if not Config.ENABLE_FILE_OPS:
        logger.warning("尝试删除文件/目录，但文件操作功能已禁用")
        return jsonify({'success': False, 'message': '文件操作功能已禁用'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    path = data.get('path', '')
    
    # 验证路径安全性
    is_safe, result = validate_path_safety(path)
    if not is_safe:
        return jsonify({'success': False, 'message': result}), 400
    
    full_path = result
    
    logger.info(f"尝试删除: {path}")
    
    # 检查路径是否存在
    if not os.path.exists(full_path):
        logger.warning(f"要删除的文件或目录不存在: {full_path}")
        return jsonify({'success': False, 'message': '文件或目录不存在'}), 404
    
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
    except PermissionError:
        logger.error(f"没有权限删除: {full_path}")
        return jsonify({'success': False, 'message': '没有权限删除此文件或目录'}), 403
    except Exception as e:
        logger.error(f"删除失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': '删除操作失败，请稍后重试'}), 500

@app.route('/api/create_folder', methods=['POST'])
@limiter.limit("20 per minute")
def create_folder():
    """创建新文件夹"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    parent_dir = data.get('path', '')
    folder_name = data.get('name', '')
    
    # 检查文件夹名是否有效
    if not folder_name or folder_name.strip() == '':
        return jsonify({'success': False, 'message': '文件夹名不能为空'}), 400
    
    # 检查文件夹名是否包含非法字符
    invalid_chars = '<>:"|?*'
    if any(char in folder_name for char in invalid_chars):
        return jsonify({'success': False, 'message': f'文件夹名不能包含以下字符: {invalid_chars}'}), 400
    
    # 验证父目录路径安全性
    is_safe, result = validate_path_safety(parent_dir)
    if not is_safe:
        return jsonify({'success': False, 'message': result}), 400
    
    full_parent_dir = result
    full_path = os.path.join(full_parent_dir, folder_name)
    
    # 检查父目录是否存在
    if not os.path.exists(full_parent_dir) or not os.path.isdir(full_parent_dir):
        return jsonify({'success': False, 'message': '父目录不存在'}), 404
    
    # 检查文件夹是否已存在
    if os.path.exists(full_path):
        return jsonify({'success': False, 'message': f'文件夹 {folder_name} 已存在'}), 409
    
    try:
        # 创建文件夹
        os.makedirs(full_path)
        logger.info(f"文件夹创建成功: {full_path}")
        
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
        logger.error(f"创建文件夹失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/rename', methods=['POST'])
@limiter.limit("20 per minute")
def rename_item():
    """重命名文件或目录"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '无效的请求数据'}), 400
    
    path = data.get('path', '')
    new_name = data.get('new_name', '')
    
    # 检查新名称是否有效
    if not new_name or new_name.strip() == '':
        return jsonify({'success': False, 'message': '新名称不能为空'}), 400
    
    # 检查新名称是否包含非法字符
    invalid_chars = '<>:"|?*'
    if any(char in new_name for char in invalid_chars):
        return jsonify({'success': False, 'message': f'新名称不能包含以下字符: {invalid_chars}'}), 400
    
    # 验证路径安全性
    is_safe, result = validate_path_safety(path)
    if not is_safe:
        return jsonify({'success': False, 'message': result}), 400
    
    full_path = result
    
    # 检查路径是否存在
    if not os.path.exists(full_path):
        return jsonify({'success': False, 'message': '文件或目录不存在'}), 404
    
    try:
        # 获取父目录和新路径
        parent_dir = os.path.dirname(full_path)
        new_path = os.path.join(parent_dir, new_name)
        
        # 检查新路径是否已存在
        if os.path.exists(new_path):
            return jsonify({'success': False, 'message': f'已存在同名文件或目录: {new_name}'}), 409
        
        # 重命名文件或目录
        os.rename(full_path, new_path)
        logger.info(f"重命名成功: {full_path} -> {new_path}")
        
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
        logger.error(f"重命名失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        
        # 获取磁盘使用情况
        disk_usage = psutil.disk_usage(ROOT_DIR)
        
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        
        system_info = {
            'success': True,
            'system': {
                'platform': sys.platform,
                'python_version': sys.version,
                'root_directory': ROOT_DIR
            },
            'storage': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent
            },
            'config': {
                'app_name': Config.APP_NAME,
                'version': '2.0.0',
                'environment': Config.ENV
            }
        }
        
        return jsonify(system_info)
    except ImportError:
        # 如果没有psutil，返回基本信息
        return jsonify({
            'success': True,
            'system': {
                'platform': sys.platform,
                'python_version': sys.version,
                'root_directory': ROOT_DIR
            },
            'config': {
                'app_name': Config.APP_NAME,
                'version': '2.0.0',
                'environment': Config.ENV
            },
            'note': '安装 psutil 包可获取更详细的系统信息'
        })
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

# 错误处理
@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'success': False, 'message': '上传的文件过大'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'success': False, 'message': '请求的资源不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    logger.error(f"内部服务器错误: {str(e)}")
    return jsonify({'success': False, 'message': '内部服务器错误'}), 500

if __name__ == '__main__':
    try:
        logger.info(f"启动文件管理系统，端口: {Config.SERVER_PORT}")
        app.run(debug=Config.DEBUG_MODE, host=Config.SERVER_HOST, port=Config.SERVER_PORT)
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
        sys.exit(1)