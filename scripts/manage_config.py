#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理脚本
用于管理配置文件，包括创建、备份、恢复等操作
"""

import os
import sys
import yaml
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, name: str = None) -> str:
        """创建配置备份"""
        if name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"config_backup_{timestamp}"
        
        backup_path = self.backup_dir / name
        backup_path.mkdir(exist_ok=True)
        
        # 复制配置文件
        config_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.txt"))
        for config_file in config_files:
            if config_file.is_file():
                shutil.copy2(config_file, backup_path / config_file.name)
        
        print(f"✅ 配置备份已创建: {backup_path}")
        return str(backup_path)
    
    def list_backups(self) -> List[str]:
        """列出所有备份"""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                backups.append(backup_dir.name)
        
        return sorted(backups, reverse=True)
    
    def restore_backup(self, name: str) -> bool:
        """恢复配置备份"""
        backup_path = self.backup_dir / name
        if not backup_path.exists():
            print(f"❌ 备份不存在: {name}")
            return False
        
        # 创建当前配置的备份
        current_backup = self.create_backup(f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # 恢复配置
        for config_file in backup_path.glob("*"):
            if config_file.is_file():
                target_file = self.config_dir / config_file.name
                shutil.copy2(config_file, target_file)
                print(f"📄 已恢复: {config_file.name}")
        
        print(f"✅ 配置已从备份恢复: {name}")
        print(f"📁 当前配置已备份到: {current_backup}")
        return True
    
    def delete_backup(self, name: str) -> bool:
        """删除配置备份"""
        backup_path = self.backup_dir / name
        if not backup_path.exists():
            print(f"❌ 备份不存在: {name}")
            return False
        
        shutil.rmtree(backup_path)
        print(f"✅ 备份已删除: {name}")
        return True
    
    def export_config(self, format: str = "json", output_file: str = None) -> str:
        """导出配置"""
        config_data = {}
        
        # 读取主配置文件
        main_config_file = self.config_dir / "config.yaml"
        if main_config_file.exists():
            with open(main_config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        
        # 读取环境文件
        env_file = self.config_dir / "environment.txt"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                config_data['current_environment'] = f.read().strip()
        
        # 导出配置
        if format == "json":
            output = json.dumps(config_data, indent=2, ensure_ascii=False)
            ext = ".json"
        elif format == "yaml":
            output = yaml.dump(config_data, default_flow_style=False, allow_unicode=True)
            ext = ".yaml"
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        # 保存到文件
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"config_export_{timestamp}{ext}"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ 配置已导出到: {output_file}")
        return output_file
    
    def import_config(self, input_file: str, validate: bool = True) -> bool:
        """导入配置"""
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"❌ 输入文件不存在: {input_file}")
            return False
        
        # 创建备份
        self.create_backup(f"before_import_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        try:
            if input_path.suffix == ".json":
                with open(input_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            elif input_path.suffix in [".yaml", ".yml"]:
                with open(input_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            else:
                print(f"❌ 不支持的文件格式: {input_path.suffix}")
                return False
            
            # 验证配置
            if validate:
                if not self._validate_imported_config(config_data):
                    print("❌ 导入的配置验证失败")
                    return False
            
            # 保存配置
            if 'current_environment' in config_data:
                env = config_data.pop('current_environment')
                env_file = self.config_dir / "environment.txt"
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(env)
                print(f"🌍 环境设置已更新: {env}")
            
            # 保存主配置
            main_config_file = self.config_dir / "config.yaml"
            with open(main_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 配置已导入: {input_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导入配置失败: {e}")
            return False
    
    def _validate_imported_config(self, config_data: Dict[str, Any]) -> bool:
        """验证导入的配置"""
        required_sections = ['environments', 'database', 'security', 'logging']
        
        for section in required_sections:
            if section not in config_data:
                print(f"❌ 缺少必需配置节: {section}")
                return False
        
        return True
    
    def show_config_info(self):
        """显示配置信息"""
        print("📋 配置信息")
        print("=" * 50)
        
        # 显示配置文件
        config_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.txt"))
        print(f"📁 配置目录: {self.config_dir}")
        print(f"📄 配置文件数量: {len(config_files)}")
        
        for config_file in sorted(config_files):
            size = config_file.stat().st_size
            mtime = datetime.fromtimestamp(config_file.stat().st_mtime)
            print(f"   {config_file.name} ({size} bytes, 修改时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # 显示环境信息
        env_file = self.config_dir / "environment.txt"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                env = f.read().strip()
            print(f"\n🌍 当前环境: {env}")
        
        # 显示备份信息
        backups = self.list_backups()
        print(f"\n💾 配置备份数量: {len(backups)}")
        if backups:
            print("   最近5个备份:")
            for backup in backups[:5]:
                backup_path = self.backup_dir / backup
                if backup_path.exists():
                    mtime = datetime.fromtimestamp(backup_path.stat().st_mtime)
                    print(f"   - {backup} (创建时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')})")
    
    def cleanup_old_backups(self, keep_count: int = 10):
        """清理旧备份"""
        backups = self.list_backups()
        if len(backups) <= keep_count:
            print(f"ℹ️  备份数量 ({len(backups)}) 未超过保留数量 ({keep_count})")
            return
        
        to_delete = backups[keep_count:]
        print(f"🧹 清理 {len(to_delete)} 个旧备份...")
        
        for backup_name in to_delete:
            self.delete_backup(backup_name)
        
        print(f"✅ 清理完成，保留 {keep_count} 个最新备份")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="配置管理工具")
    parser.add_argument("--config-dir", default="config", help="配置目录路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 备份命令
    backup_parser = subparsers.add_parser("backup", help="创建配置备份")
    backup_parser.add_argument("--name", help="备份名称")
    
    # 恢复命令
    restore_parser = subparsers.add_parser("restore", help="恢复配置备份")
    restore_parser.add_argument("name", help="备份名称")
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="列出所有备份")
    
    # 删除命令
    delete_parser = subparsers.add_parser("delete", help="删除配置备份")
    delete_parser.add_argument("name", help="备份名称")
    
    # 导出命令
    export_parser = subparsers.add_parser("export", help="导出配置")
    export_parser.add_argument("--format", choices=["json", "yaml"], default="json", help="导出格式")
    export_parser.add_argument("--output", help="输出文件路径")
    
    # 导入命令
    import_parser = subparsers.add_parser("import", help="导入配置")
    import_parser.add_argument("file", help="输入文件路径")
    import_parser.add_argument("--no-validate", action="store_true", help="跳过验证")
    
    # 信息命令
    info_parser = subparsers.add_parser("info", help="显示配置信息")
    
    # 清理命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧备份")
    cleanup_parser.add_argument("--keep", type=int, default=10, help="保留备份数量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建配置管理器
    config_manager = ConfigManager(args.config_dir)
    
    try:
        if args.command == "backup":
            backup_path = config_manager.create_backup(args.name)
            print(f"备份路径: {backup_path}")
        
        elif args.command == "restore":
            config_manager.restore_backup(args.name)
        
        elif args.command == "list":
            backups = config_manager.list_backups()
            if backups:
                print("📋 可用备份:")
                for backup in backups:
                    print(f"   - {backup}")
            else:
                print("ℹ️  没有可用的备份")
        
        elif args.command == "delete":
            config_manager.delete_backup(args.name)
        
        elif args.command == "export":
            output_file = config_manager.export_config(args.format, args.output)
            print(f"导出文件: {output_file}")
        
        elif args.command == "import":
            config_manager.import_config(args.file, not args.no_validate)
        
        elif args.command == "info":
            config_manager.show_config_info()
        
        elif args.command == "cleanup":
            config_manager.cleanup_old_backups(args.keep)
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
