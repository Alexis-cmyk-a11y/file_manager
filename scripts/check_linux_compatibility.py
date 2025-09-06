#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux兼容性检查脚本
检查文件管理系统在Linux系统上的兼容性
"""

import os
import sys
import platform
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple

class LinuxCompatibilityChecker:
    """Linux兼容性检查器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def log_success(self, message: str):
        """记录成功信息"""
        print(f"✅ {message}")
        self.success_count += 1
        self.total_checks += 1
    
    def log_warning(self, message: str):
        """记录警告信息"""
        print(f"⚠️  {message}")
        self.warnings.append(message)
        self.total_checks += 1
    
    def log_error(self, message: str):
        """记录错误信息"""
        print(f"❌ {message}")
        self.issues.append(message)
        self.total_checks += 1
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("\n🐍 检查Python版本...")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 8:
            self.log_success(f"Python版本 {version.major}.{version.minor}.{version.micro} 符合要求")
            return True
        else:
            self.log_error(f"Python版本 {version.major}.{version.minor}.{version.micro} 过低，需要3.8+")
            return False
    
    def check_operating_system(self) -> bool:
        """检查操作系统"""
        print("\n🖥️  检查操作系统...")
        
        system = platform.system()
        if system == "Linux":
            self.log_success(f"操作系统: {system} - 完全兼容")
            return True
        elif system == "Windows":
            self.log_warning(f"当前操作系统: {system} - 建议在Linux上运行")
            return False
        else:
            self.log_warning(f"操作系统: {system} - 未测试，可能存在兼容性问题")
            return False
    
    def check_required_packages(self) -> bool:
        """检查必需的Python包"""
        print("\n📦 检查Python依赖包...")
        
        required_packages = [
            'flask', 'yaml', 'redis', 'pymysql', 'sqlalchemy',
            'werkzeug', 'flask_cors', 'flask_limiter', 'flask_session',
            'bcrypt', 'requests', 'psutil', 'cryptography'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
                self.log_success(f"包 {package} 已安装")
            except ImportError:
                missing_packages.append(package)
                self.log_error(f"包 {package} 未安装")
        
        if missing_packages:
            print(f"\n缺少的包: {', '.join(missing_packages)}")
            print("请运行: pip install -r requirements.txt")
            return False
        
        return True
    
    def check_file_paths(self) -> bool:
        """检查文件路径兼容性"""
        print("\n📁 检查文件路径兼容性...")
        
        # 检查配置文件中的路径
        config_file = self.project_root / "config" / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "C:/" in content or "C:\\" in content:
                    self.log_warning("配置文件中包含Windows路径，需要修改为Linux路径")
                    return False
                else:
                    self.log_success("配置文件路径兼容Linux")
        
        # 检查Python文件中的路径（排除检查脚本本身）
        python_files = list(self.project_root.rglob("*.py"))
        windows_paths = []
        
        for py_file in python_files:
            # 跳过检查脚本本身
            if "check_linux_compatibility.py" in str(py_file):
                continue
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "C:/" in content or "C:\\" in content:
                        windows_paths.append(str(py_file))
            except Exception:
                continue
        
        if windows_paths:
            self.log_warning(f"以下Python文件包含Windows路径: {', '.join(windows_paths)}")
            return False
        else:
            self.log_success("Python文件路径兼容Linux")
        
        return True
    
    def check_file_permissions(self) -> bool:
        """检查文件权限"""
        print("\n🔐 检查文件权限...")
        
        # 检查关键目录的权限
        key_directories = [
            "logs", "temp", "download", "static", "templates"
        ]
        
        for directory in key_directories:
            dir_path = self.project_root / directory
            if dir_path.exists():
                if os.access(dir_path, os.R_OK | os.W_OK):
                    self.log_success(f"目录 {directory} 权限正常")
                else:
                    self.log_error(f"目录 {directory} 权限不足")
                    return False
            else:
                self.log_warning(f"目录 {directory} 不存在")
        
        return True
    
    def check_script_compatibility(self) -> bool:
        """检查脚本兼容性"""
        print("\n📜 检查脚本兼容性...")
        
        # 检查Python脚本的shebang
        python_scripts = [
            "main.py", "scripts/init_database.py", "scripts/start.py",
            "scripts/validate_config.py", "scripts/manage_config.py"
        ]
        
        for script in python_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                with open(script_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("#!/usr/bin/env python3"):
                        self.log_success(f"脚本 {script} shebang正确")
                    else:
                        self.log_warning(f"脚本 {script} shebang可能不正确")
        
        # 检查shell脚本
        shell_scripts = ["scripts/setup_linux.sh", "scripts/deploy_linux.sh"]
        for script in shell_scripts:
            script_path = self.project_root / script
            if script_path.exists():
                if os.access(script_path, os.X_OK):
                    self.log_success(f"Shell脚本 {script} 可执行")
                else:
                    self.log_warning(f"Shell脚本 {script} 不可执行")
        
        return True
    
    def check_database_compatibility(self) -> bool:
        """检查数据库兼容性"""
        print("\n🗄️  检查数据库兼容性...")
        
        # 检查MySQL连接配置
        try:
            import pymysql
            self.log_success("PyMySQL包可用")
        except ImportError:
            self.log_error("PyMySQL包不可用")
            return False
        
        # 检查Redis连接配置
        try:
            import redis
            self.log_success("Redis包可用")
        except ImportError:
            self.log_error("Redis包不可用")
            return False
        
        return True
    
    def check_web_server_compatibility(self) -> bool:
        """检查Web服务器兼容性"""
        print("\n🌐 检查Web服务器兼容性...")
        
        # 检查Flask配置
        try:
            from flask import Flask
            self.log_success("Flask框架可用")
        except ImportError:
            self.log_error("Flask框架不可用")
            return False
        
        # 检查Nginx配置
        nginx_config = self.project_root / "nginx.conf"
        if nginx_config.exists():
            with open(nginx_config, 'r', encoding='utf-8') as f:
                content = f.read()
                if "user nginx;" in content:
                    self.log_success("Nginx配置文件兼容Linux")
                else:
                    self.log_warning("Nginx配置文件可能需要调整")
        
        return True
    
    def check_network_compatibility(self) -> bool:
        """检查网络兼容性"""
        print("\n🌍 检查网络兼容性...")
        
        # 检查端口配置
        config_file = self.project_root / "config" / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "port: 8888" in content:
                    self.log_success("端口配置正常")
                else:
                    self.log_warning("端口配置可能需要检查")
        
        return True
    
    def check_security_compatibility(self) -> bool:
        """检查安全兼容性"""
        print("\n🔒 检查安全兼容性...")
        
        # 检查安全服务
        security_service = self.project_root / "services" / "security_service.py"
        if security_service.exists():
            self.log_success("安全服务模块存在")
        else:
            self.log_error("安全服务模块不存在")
            return False
        
        # 检查文件权限验证
        file_utils = self.project_root / "utils" / "file_utils.py"
        if file_utils.exists():
            with open(file_utils, 'r', encoding='utf-8') as f:
                content = f.read()
                if "is_safe_path" in content:
                    self.log_success("文件路径安全检查功能存在")
                else:
                    self.log_warning("文件路径安全检查功能可能不完整")
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """生成检查报告"""
        print("\n" + "="*60)
        print("📊 Linux兼容性检查报告")
        print("="*60)
        
        success_rate = (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"总检查项: {self.total_checks}")
        print(f"成功项: {self.success_count}")
        print(f"警告项: {len(self.warnings)}")
        print(f"错误项: {len(self.issues)}")
        print(f"成功率: {success_rate:.1f}%")
        
        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        if not self.issues:
            print(f"\n🎉 恭喜！系统完全兼容Linux")
            print("可以安全部署到Linux环境")
        elif len(self.issues) <= 2:
            print(f"\n✅ 系统基本兼容Linux，有少量问题需要解决")
        else:
            print(f"\n⚠️  系统存在较多兼容性问题，需要修复后再部署")
        
        return {
            'total_checks': self.total_checks,
            'success_count': self.success_count,
            'warning_count': len(self.warnings),
            'error_count': len(self.issues),
            'success_rate': success_rate,
            'issues': self.issues,
            'warnings': self.warnings,
            'compatible': len(self.issues) == 0
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        print("🚀 开始Linux兼容性检查...")
        print("="*60)
        
        # 运行所有检查
        checks = [
            self.check_python_version,
            self.check_operating_system,
            self.check_required_packages,
            self.check_file_paths,
            self.check_file_permissions,
            self.check_script_compatibility,
            self.check_database_compatibility,
            self.check_web_server_compatibility,
            self.check_network_compatibility,
            self.check_security_compatibility
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.log_error(f"检查过程中发生错误: {e}")
        
        # 生成报告
        return self.generate_report()

def main():
    """主函数"""
    checker = LinuxCompatibilityChecker()
    report = checker.run_all_checks()
    
    # 根据检查结果设置退出码
    if report['compatible']:
        sys.exit(0)  # 完全兼容
    elif report['error_count'] <= 2:
        sys.exit(1)  # 基本兼容，有少量问题
    else:
        sys.exit(2)  # 存在较多问题

if __name__ == '__main__':
    main()
