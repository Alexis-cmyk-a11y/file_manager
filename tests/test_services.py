"""
服务层测试
测试各种服务类的功能
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.file_service import FileService
from services.security_service import SecurityService
from services.upload_service import UploadService
from services.download_service import DownloadService
from services.system_service import SystemService

class TestSecurityService(unittest.TestCase):
    """安全服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.security_service = SecurityService()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_path_safety_empty_path(self):
        """测试空路径验证"""
        is_safe, result = self.security_service.validate_path_safety("")
        self.assertTrue(is_safe)
        self.assertEqual(result, self.security_service.config.ROOT_DIR)
    
    def test_validate_path_safety_traversal_attack(self):
        """测试路径遍历攻击防护"""
        is_safe, result = self.security_service.validate_path_safety("../etc/passwd")
        self.assertFalse(is_safe)
        self.assertEqual(result, "无效的路径")
    
    def test_validate_path_safety_valid_path(self):
        """测试有效路径验证"""
        test_path = "test_folder"
        is_safe, result = self.security_service.validate_path_safety(test_path)
        self.assertTrue(is_safe)
        expected_path = os.path.join(self.security_service.config.ROOT_DIR, test_path)
        self.assertEqual(result, expected_path)

class TestFileService(unittest.TestCase):
    """文件服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.file_service = FileService()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_folder(self):
        """测试创建文件夹"""
        folder_name = "test_folder"
        result = self.file_service.create_folder(self.temp_dir, folder_name)
        self.assertTrue(result['success'])
        self.assertIn('folder', result)
        
        # 验证文件夹是否真的被创建
        folder_path = os.path.join(self.temp_dir, folder_name)
        self.assertTrue(os.path.exists(folder_path))
        self.assertTrue(os.path.isdir(folder_path))

class TestSystemService(unittest.TestCase):
    """系统服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.system_service = SystemService()
    
    def test_get_system_info(self):
        """测试获取系统信息"""
        result = self.system_service.get_system_info()
        self.assertTrue(result['success'])
        self.assertIn('system', result)
        self.assertIn('config', result)
        self.assertEqual(result['config']['version'], '2.0.0')

if __name__ == '__main__':
    unittest.main()
