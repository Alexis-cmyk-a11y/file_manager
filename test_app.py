"""
文件管理系统测试文件
用于测试各个功能模块
"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import FileUtils, SecurityUtils, PathUtils, TimeUtils

class TestFileUtils(unittest.TestCase):
    """测试文件工具类"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        
        # 创建测试文件
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write("测试内容")
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_get_file_size_display(self):
        """测试文件大小显示"""
        self.assertEqual(FileUtils.get_file_size_display(0), "0 B")
        self.assertEqual(FileUtils.get_file_size_display(1024), "1.0 KB")
        self.assertEqual(FileUtils.get_file_size_display(1024*1024), "1.0 MB")
        self.assertEqual(FileUtils.get_file_size_display(1024*1024*1024), "1.0 GB")
    
    def test_get_file_icon(self):
        """测试文件图标获取"""
        self.assertEqual(FileUtils.get_file_icon("test.jpg"), "fa-image")
        self.assertEqual(FileUtils.get_file_icon("test.pdf"), "fa-file-text")
        self.assertEqual(FileUtils.get_file_icon("test.zip"), "fa-archive")
        self.assertEqual(FileUtils.get_file_icon("test.py"), "fa-code")
        self.assertEqual(FileUtils.get_file_icon("test.exe"), "fa-cog")
        self.assertEqual(FileUtils.get_file_icon("test.unknown"), "fa-file")
    
    def test_is_image_file(self):
        """测试图片文件判断"""
        self.assertTrue(FileUtils.is_image_file("test.jpg"))
        self.assertTrue(FileUtils.is_image_file("test.png"))
        self.assertFalse(FileUtils.is_image_file("test.txt"))
        self.assertFalse(FileUtils.is_image_file("test.pdf"))
    
    def test_is_text_file(self):
        """测试文本文件判断"""
        self.assertTrue(FileUtils.is_text_file("test.txt"))
        self.assertTrue(FileUtils.is_text_file("test.py"))
        self.assertFalse(FileUtils.is_text_file("test.jpg"))
        self.assertFalse(FileUtils.is_text_file("test.zip"))
    
    def test_get_mime_type(self):
        """测试MIME类型获取"""
        self.assertEqual(FileUtils.get_mime_type("test.txt"), "text/plain")
        self.assertEqual(FileUtils.get_mime_type("test.jpg"), "image/jpeg")
        self.assertEqual(FileUtils.get_mime_type("test.unknown"), "application/octet-stream")
    
    def test_calculate_file_hash(self):
        """测试文件哈希计算"""
        # 计算MD5哈希
        md5_hash = FileUtils.calculate_file_hash(self.test_file, 'md5')
        self.assertIsNotNone(md5_hash)
        self.assertEqual(len(md5_hash), 32)  # MD5哈希长度为32位
        
        # 计算SHA1哈希
        sha1_hash = FileUtils.calculate_file_hash(self.test_file, 'sha1')
        self.assertIsNotNone(sha1_hash)
        self.assertEqual(len(sha1_hash), 40)  # SHA1哈希长度为40位
        
        # 测试不支持的算法
        with self.assertRaises(ValueError):
            FileUtils.calculate_file_hash(self.test_file, 'invalid')

class TestSecurityUtils(unittest.TestCase):
    """测试安全工具类"""
    
    def test_sanitize_filename(self):
        """测试文件名清理"""
        dangerous_name = 'file<>:"|?*.txt'
        safe_name = SecurityUtils.sanitize_filename(dangerous_name)
        self.assertNotIn('<', safe_name)
        self.assertNotIn('>', safe_name)
        self.assertNotIn(':', safe_name)
        self.assertNotIn('"', safe_name)
        self.assertNotIn('|', safe_name)
        self.assertNotIn('?', safe_name)
        self.assertNotIn('*', safe_name)
    
    def test_is_safe_file_type(self):
        """测试文件类型安全检查"""
        # 测试允许的文件类型
        allowed_exts = {'.txt', '.pdf', '.jpg'}
        result, message = SecurityUtils.is_safe_file_type("test.txt", allowed_exts)
        self.assertTrue(result)
        
        # 测试禁止的文件类型
        forbidden_exts = {'.exe', '.bat'}
        result, message = SecurityUtils.is_safe_file_type("test.exe", forbidden_exts)
        self.assertFalse(result)
        self.assertIn("不允许上传", message)
        
        # 测试不在允许列表中的文件类型
        result, message = SecurityUtils.is_safe_file_type("test.unknown", allowed_exts)
        self.assertFalse(result)
        self.assertIn("只允许上传", message)
    
    def test_validate_file_size(self):
        """测试文件大小验证"""
        max_size = 1024 * 1024  # 1MB
        
        # 测试正常大小
        result, message = SecurityUtils.validate_file_size(512 * 1024, max_size)
        self.assertTrue(result)
        
        # 测试超过限制的大小
        result, message = SecurityUtils.validate_file_size(2 * 1024 * 1024, max_size)
        self.assertFalse(result)
        self.assertIn("超过限制", message)

class TestPathUtils(unittest.TestCase):
    """测试路径工具类"""
    
    def test_normalize_path(self):
        """测试路径标准化"""
        # 测试Windows路径
        windows_path = "C:\\Users\\test\\file.txt"
        normalized = PathUtils.normalize_path(windows_path)
        self.assertNotIn('\\', normalized)
        
        # 测试多余斜杠
        path_with_double_slash = "path//to//file"
        normalized = PathUtils.normalize_path(path_with_double_slash)
        self.assertNotIn('//', normalized)
        
        # 测试末尾斜杠
        path_with_trailing_slash = "path/to/file/"
        normalized = PathUtils.normalize_path(path_with_trailing_slash)
        self.assertFalse(normalized.endswith('/'))
        
        # 测试根目录
        root_path = "/"
        normalized = PathUtils.normalize_path(root_path)
        self.assertEqual(normalized, "/")
    
    def test_get_relative_path(self):
        """测试相对路径获取"""
        base_path = "/home/user"
        full_path = "/home/user/documents/file.txt"
        relative = PathUtils.get_relative_path(full_path, base_path)
        self.assertEqual(relative, "documents/file.txt")
    
    def test_is_subpath(self):
        """测试子路径检查"""
        base_path = "/home/user"
        
        # 测试是子路径
        sub_path = "/home/user/documents"
        self.assertTrue(PathUtils.is_subpath(sub_path, base_path))
        
        # 测试不是子路径
        other_path = "/home/other"
        self.assertFalse(PathUtils.is_subpath(other_path, base_path))
    
    def test_get_path_depth(self):
        """测试路径深度获取"""
        self.assertEqual(PathUtils.get_path_depth(""), 0)
        self.assertEqual(PathUtils.get_path_depth("/"), 0)
        self.assertEqual(PathUtils.get_path_depth("path"), 1)
        self.assertEqual(PathUtils.get_path_depth("path/to/file"), 3)
    
    def test_get_parent_path(self):
        """测试父路径获取"""
        self.assertEqual(PathUtils.get_parent_path(""), "")
        self.assertEqual(PathUtils.get_parent_path("file"), "")
        self.assertEqual(PathUtils.get_parent_path("path/file"), "path")
        self.assertEqual(PathUtils.get_parent_path("path/to/file"), "path/to")

class TestTimeUtils(unittest.TestCase):
    """测试时间工具类"""
    
    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 测试当前时间
        now = int(os.time())
        formatted = TimeUtils.format_timestamp(now)
        self.assertIn("今天", formatted)
        
        # 测试昨天
        yesterday = now - 24 * 3600
        formatted = TimeUtils.format_timestamp(yesterday)
        self.assertIn("昨天", formatted)
    
    def test_get_file_age_display(self):
        """测试文件年龄显示"""
        now = int(os.time())
        
        # 测试刚刚
        age = TimeUtils.get_file_age_display(now)
        self.assertEqual(age, "刚刚")
        
        # 测试分钟前
        one_minute_ago = now - 60
        age = TimeUtils.get_file_age_display(one_minute_ago)
        self.assertIn("分钟前", age)
        
        # 测试小时前
        one_hour_ago = now - 3600
        age = TimeUtils.get_file_age_display(one_hour_ago)
        self.assertIn("小时前", age)
        
        # 测试天前
        one_day_ago = now - 24 * 3600
        age = TimeUtils.get_file_age_display(one_day_ago)
        self.assertIn("天前", age)

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # 创建测试文件
        for i in range(3):
            filename = f"test_file_{i}.txt"
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"测试内容 {i}")
            self.test_files.append(filepath)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_file_operations_integration(self):
        """测试文件操作集成"""
        # 测试文件信息获取
        for filepath in self.test_files:
            # 获取文件大小
            size = os.path.getsize(filepath)
            size_display = FileUtils.get_file_size_display(size)
            self.assertIsInstance(size_display, str)
            
            # 获取文件图标
            icon = FileUtils.get_file_icon(os.path.basename(filepath))
            self.assertIsInstance(icon, str)
            
            # 计算文件哈希
            hash_value = FileUtils.calculate_file_hash(filepath, 'md5')
            self.assertIsNotNone(hash_value)
            
            # 验证文件类型
            is_safe, message = SecurityUtils.is_safe_file_type(
                os.path.basename(filepath), 
                {'.txt', '.pdf'}
            )
            self.assertTrue(is_safe)
    
    def test_path_operations_integration(self):
        """测试路径操作集成"""
        # 创建嵌套目录结构
        nested_dir = os.path.join(self.temp_dir, "nested", "deep", "path")
        os.makedirs(nested_dir, exist_ok=True)
        
        # 测试路径标准化
        normalized = PathUtils.normalize_path(nested_dir.replace('\\', '/'))
        self.assertNotIn('\\', normalized)
        
        # 测试路径深度
        depth = PathUtils.get_path_depth(normalized)
        self.assertGreater(depth, 0)
        
        # 测试子路径检查
        is_sub = PathUtils.is_subpath(nested_dir, self.temp_dir)
        self.assertTrue(is_sub)
        
        # 测试父路径获取
        parent = PathUtils.get_parent_path(normalized)
        self.assertNotEqual(parent, normalized)

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestFileUtils,
        TestSecurityUtils,
        TestPathUtils,
        TestTimeUtils,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    print("开始运行文件管理系统测试...")
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)
