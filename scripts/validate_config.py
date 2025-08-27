#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件验证脚本
验证配置文件的格式、结构和有效性
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def validate_yaml_file(file_path: Path) -> Tuple[bool, List[str]]:
    """验证YAML文件格式"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
        
        if content is None:
            errors.append("文件内容为空")
            return False, errors
            
        return True, errors
        
    except yaml.YAMLError as e:
        errors.append(f"YAML格式错误: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"读取文件失败: {e}")
        return False, errors

def validate_config_structure(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证配置结构"""
    errors = []
    warnings = []
    
    # 必需配置项
    required_sections = ['environments', 'database', 'security', 'logging']
    for section in required_sections:
        if section not in config:
            errors.append(f"缺少必需配置节: {section}")
    
    # 验证环境配置
    if 'environments' in config:
        environments = config['environments']
        if not isinstance(environments, dict):
            errors.append("environments必须是字典类型")
        else:
            for env_name, env_config in environments.items():
                if not isinstance(env_config, dict):
                    errors.append(f"环境 {env_name} 配置必须是字典类型")
                else:
                    # 验证环境特定配置
                    if 'server' in env_config:
                        server = env_config['server']
                        if 'port' in server:
                            port = server['port']
                            if not isinstance(port, int) or not (1 <= port <= 65535):
                                errors.append(f"环境 {env_name} 的端口必须在1-65535之间: {port}")
                    
                    if 'limits' in env_config:
                        limits = env_config['limits']
                        if 'max_file_size' in limits:
                            max_size = limits['max_file_size']
                            if not isinstance(max_size, int) or max_size <= 0:
                                errors.append(f"环境 {env_name} 的最大文件大小必须大于0: {max_size}")
    
    # 验证数据库配置
    if 'database' in config:
        db_config = config['database']
        if 'mysql' not in db_config:
            errors.append("缺少MySQL数据库配置")
        if 'redis' not in db_config:
            errors.append("缺少Redis配置")
    
    # 验证安全配置
    if 'security' in config:
        security = config['security']
        if 'session_timeout' in security:
            timeout = security['session_timeout']
            if not isinstance(timeout, int) or timeout <= 0:
                errors.append(f"会话超时必须大于0: {timeout}")
    
    # 验证日志配置
    if 'logging' in config:
        logging_config = config['logging']
        if 'level' in logging_config:
            level = logging_config['level']
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level not in valid_levels:
                warnings.append(f"日志级别 {level} 不是标准级别，建议使用: {', '.join(valid_levels)}")
    
    # 验证前端配置
    if 'frontend' in config:
        frontend = config['frontend']
        if 'theme' in frontend:
            theme = frontend['theme']
            if 'primary_color' in theme:
                color = theme['primary_color']
                if not color.startswith('#') or len(color) != 7:
                    warnings.append(f"主色调格式可能不正确: {color}")
    
    return len(errors) == 0, errors + warnings

def validate_environment_file(env_file: Path, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """验证环境特定配置文件"""
    errors = []
    
    # 检查环境名称是否在主配置中定义
    env_name = env_file.stem
    if 'environments' not in config:
        errors.append("主配置中缺少environments节")
    elif env_name not in config['environments']:
        errors.append(f"环境 {env_name} 在主配置中未定义")
    
    return len(errors) == 0, errors

def validate_config_files(config_dir: Path) -> Tuple[bool, List[str]]:
    """验证所有配置文件"""
    all_errors = []
    all_warnings = []
    
    print(f"🔍 验证配置目录: {config_dir}")
    print("=" * 50)
    
    # 验证主配置文件
    main_config_file = config_dir / "config.yaml"
    if main_config_file.exists():
        print(f"📋 验证主配置文件: {main_config_file.name}")
        
        # 验证YAML格式
        is_valid, errors = validate_yaml_file(main_config_file)
        if not is_valid:
            all_errors.extend(errors)
            print(f"❌ YAML格式验证失败")
            for error in errors:
                print(f"   - {error}")
        else:
            print("✅ YAML格式验证通过")
            
            # 验证配置结构
            with open(main_config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            is_valid, issues = validate_config_structure(config)
            if not is_valid:
                all_errors.extend(issues)
                print(f"❌ 配置结构验证失败")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print("✅ 配置结构验证通过")
                
                # 验证环境特定配置文件
                for env_file in config_dir.glob("*.yaml"):
                    if env_file.name != "config.yaml":
                        print(f"\n🌍 验证环境配置文件: {env_file.name}")
                        
                        # 验证YAML格式
                        is_valid, errors = validate_yaml_file(env_file)
                        if not is_valid:
                            all_errors.extend(errors)
                            print(f"❌ YAML格式验证失败")
                            for error in errors:
                                print(f"   - {error}")
                        else:
                            print("✅ YAML格式验证通过")
                            
                            # 验证环境配置
                            is_valid, issues = validate_environment_file(env_file, config)
                            if not is_valid:
                                all_errors.extend(issues)
                                print(f"❌ 环境配置验证失败")
                                for issue in issues:
                                    print(f"   - {issue}")
                            else:
                                print("✅ 环境配置验证通过")
    else:
        all_errors.append("主配置文件 config.yaml 不存在")
        print("❌ 主配置文件不存在")
    
    # 验证环境文件
    env_file = config_dir / "environment.txt"
    if env_file.exists():
        print(f"\n🌍 验证环境文件: {env_file.name}")
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                env = f.read().strip()
            
            valid_envs = ['development', 'production', 'testing']
            if env in valid_envs:
                print(f"✅ 环境设置有效: {env}")
            else:
                all_errors.append(f"环境设置无效: {env}，有效值: {', '.join(valid_envs)}")
                print(f"❌ 环境设置无效: {env}")
        except Exception as e:
            all_errors.append(f"读取环境文件失败: {e}")
            print(f"❌ 读取环境文件失败: {e}")
    else:
        all_warnings.append("环境文件 environment.txt 不存在，将使用默认环境")
        print("⚠️  环境文件不存在，将使用默认环境")
    
    # 验证其他配置文件
    other_configs = ['app.yaml', 'tencent_cloud.py', 'tencent_cloud.template.py']
    for config_name in other_configs:
        config_file = config_dir / config_name
        if config_file.exists():
            print(f"\n📄 检查配置文件: {config_file.name}")
            if config_file.suffix == '.yaml':
                is_valid, errors = validate_yaml_file(config_file)
                if is_valid:
                    print("✅ YAML格式验证通过")
                else:
                    all_warnings.extend(errors)
                    print("⚠️  YAML格式验证失败（非必需文件）")
            else:
                print("ℹ️  非YAML配置文件，跳过验证")
    
    return len(all_errors) == 0, all_errors + all_warnings

def main():
    """主函数"""
    config_dir = Path("config")
    
    if not config_dir.exists():
        print(f"❌ 配置目录不存在: {config_dir}")
        sys.exit(1)
    
    # 验证配置文件
    is_valid, issues = validate_config_files(config_dir)
    
    print("\n" + "=" * 50)
    print("📊 验证结果摘要")
    print("=" * 50)
    
    if is_valid:
        print("✅ 所有配置文件验证通过！")
        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个警告:")
            for issue in issues:
                print(f"   - {issue}")
    else:
        print(f"❌ 发现 {len(issues)} 个问题:")
        for issue in issues:
            print(f"   - {issue}")
        sys.exit(1)
    
    print(f"\n🚀 配置验证完成，可以启动应用了！")

if __name__ == '__main__':
    main()
