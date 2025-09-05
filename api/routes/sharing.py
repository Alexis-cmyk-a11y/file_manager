#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件共享路由
处理文件共享相关的API请求
"""

from flask import Blueprint, request, jsonify, session
from services.sharing_service import get_sharing_service
from services.auth_service import get_auth_service
from utils.logger import get_logger
import os
from utils.auth_middleware import require_auth_api, get_current_user

logger = get_logger(__name__)
sharing_bp = Blueprint('sharing', __name__)

@sharing_bp.route('/share', methods=['POST'])
@require_auth_api
def share_file():
    """共享文件"""
    try:
        
        # 获取请求参数
        data = request.get_json()
        if not data or 'source_path' not in data:
            return jsonify({'success': False, 'message': '缺少必要参数'}), 400
        
        source_path = data['source_path']
        target_name = data.get('target_name', os.path.basename(source_path))
        
        # 获取当前用户信息
        current_user = get_current_user()
        username = current_user.get('username', current_user.get('email', '').split('@')[0])
        
        if not username:
            return jsonify({'success': False, 'message': '无法获取用户信息'}), 400
        
        # 共享文件（使用硬链接）
        sharing_service = get_sharing_service()
        success, message = sharing_service.share_file(username, source_path, target_name)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        logger.error(f"共享文件失败: {e}")
        return jsonify({'success': False, 'message': '系统错误'}), 500

@sharing_bp.route('/unshare', methods=['POST'])
@require_auth_api
def unshare_file():
    """取消共享文件"""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        file_path = data['file_path']
        current_user = get_current_user()
        username = current_user['email'].split('@')[0] if current_user and current_user.get('email') else None
        
        if not username:
            return jsonify({
                'success': False,
                'message': '无法获取用户信息'
            }), 400
        
        sharing_service = get_sharing_service()
        success, message = sharing_service.unshare_file(username, file_path)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"取消共享文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sharing_bp.route('/delete', methods=['DELETE'])
@require_auth_api
def delete_shared_file():
    """删除共享文件"""
    try:
        data = request.get_json()
        if not data or 'filename' not in data or 'owner' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        filename = data['filename']
        owner = data['owner']  # 文件所有者
        current_user = get_current_user()
        current_username = current_user['email'].split('@')[0] if current_user and current_user.get('email') else None
        
        if not current_username:
            return jsonify({
                'success': False,
                'message': '无法获取用户信息'
            }), 400
        
        # 权限检查：只有文件所有者和管理员可以删除
        if current_username != owner and current_username != 'admin':
            return jsonify({
                'success': False,
                'message': '权限不足，只有文件所有者和管理员可以删除共享文件'
            }), 403
        
        sharing_service = get_sharing_service()
        success, message = sharing_service.delete_shared_file(owner, filename)
        
        return jsonify({
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"删除共享文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sharing_bp.route('/shared', methods=['GET'])
@require_auth_api
def get_shared_files():
    """获取共享文件列表"""
    try:
        current_user = get_current_user()
        username = request.args.get('username')  # 可选参数，获取特定用户的共享文件
        
        # 获取共享文件列表
        sharing_service = get_sharing_service()
        if username:
            # 如果指定了用户名，获取该用户的共享文件
            shared_files = sharing_service.get_shared_files(username)
        else:
            # 如果没有指定用户名，获取所有共享文件
            shared_files = sharing_service.get_shared_files()
        
        return jsonify({
            'success': True, 
            'data': shared_files,
            'total': len(shared_files)
        })
        
    except Exception as e:
        logger.error(f"获取共享文件列表失败: {e}")
        return jsonify({'success': False, 'message': '系统错误'}), 500

@sharing_bp.route('/shared/<username>', methods=['GET'])
@require_auth_api
def get_user_shared_files(username):
    """获取指定用户的共享文件列表"""
    try:
        # 获取指定用户的共享文件列表
        sharing_service = get_sharing_service()
        shared_files = sharing_service.get_shared_files(username)
        
        return jsonify({
            'success': True, 
            'data': shared_files,
            'total': len(shared_files)
        })
        
    except Exception as e:
        logger.error(f"获取用户共享文件列表失败: {e}")
        return jsonify({'success': False, 'message': '系统错误'}), 500

@sharing_bp.route('/status/<username>/<path:file_path>', methods=['GET'])
@require_auth_api
def check_share_status(username, file_path):
    """检查文件共享状态"""
    try:
        # 检查文件共享状态
        sharing_service = get_sharing_service()
        is_shared = sharing_service.is_file_shared(username, file_path)
        
        return jsonify({
            'success': True, 
            'is_shared': is_shared
        })
        
    except Exception as e:
        logger.error(f"检查文件共享状态失败: {e}")
        return jsonify({'success': False, 'message': '系统错误'}), 500

@sharing_bp.route('/cleanup', methods=['POST'])
@require_auth_api
def cleanup_orphaned_shares():
    """清理孤立的共享文件（管理员功能）"""
    try:
        # 这里可以添加管理员权限检查
        # if not is_admin(session['user_id']):
        #     return jsonify({'success': False, 'message': '权限不足'}), 403
        
        # 清理孤立的共享文件
        sharing_service = get_sharing_service()
        cleaned_count = sharing_service.cleanup_orphaned_shares()
        
        return jsonify({
            'success': True, 
            'message': f'清理完成，共清理 {cleaned_count} 个孤立共享文件',
            'cleaned_count': cleaned_count
        })
        
    except Exception as e:
        logger.error(f"清理孤立共享文件失败: {e}")
        return jsonify({'success': False, 'message': '系统错误'}), 500
