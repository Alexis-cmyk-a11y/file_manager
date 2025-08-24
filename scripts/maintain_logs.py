#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
操作日志维护脚本
用于清理过期日志、优化表性能、查看日志统计信息
"""

import os
import sys
import argparse
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from services.mysql_service import get_mysql_service
from utils.logger import get_logger

logger = get_logger(__name__)

def show_log_stats():
    """显示日志统计信息"""
    try:
        mysql_service = get_mysql_service()
        if not mysql_service.is_connected():
            print("❌ MySQL服务未连接")
            return False
        
        print("📊 操作日志统计信息")
        print("=" * 50)
        
        retention_info = mysql_service.get_log_retention_info()
        if not retention_info.get('success'):
            print(f"❌ 获取日志信息失败: {retention_info.get('message')}")
            return False
        
        print(f"📈 总记录数: {retention_info['total_records']:,}")
        print(f"🕐 最早日志: {retention_info['oldest_log_time'] or '无'}")
        print(f"🕐 最新日志: {retention_info['newest_log_time'] or '无'}")
        print(f"🕐 当前时间: {retention_info['current_time']}")
        print()
        
        print("📅 各时间段记录数:")
        for label, count in retention_info['retention_stats'].items():
            print(f"   {label}: {count:,} 条")
        
        print()
        if retention_info.get('recommended_cleanup'):
            print("⚠️  建议: 记录数较多，建议进行日志清理")
        else:
            print("✅ 记录数正常，无需清理")
        
        return True
        
    except Exception as e:
        print(f"❌ 显示日志统计失败: {e}")
        return False

def cleanup_logs(retention_days=30, force=False):
    """清理过期日志"""
    try:
        mysql_service = get_mysql_service()
        if not mysql_service.is_connected():
            print("❌ MySQL服务未连接")
            return False
        
        print(f"🧹 开始清理超过{retention_days}天的操作日志...")
        print("=" * 50)
        
        # 先显示清理前的统计信息
        retention_info = mysql_service.get_log_retention_info()
        if retention_info.get('success'):
            old_count = retention_info['total_records'] - retention_info['retention_stats']['30天内']
            print(f"📊 清理前统计:")
            print(f"   总记录数: {retention_info['total_records']:,}")
            print(f"   超过{retention_days}天: {old_count:,} 条")
            print(f"   30天内: {retention_info['retention_stats']['30天内']:,} 条")
            print()
        
        if not force and old_count == 0:
            print("✅ 没有需要清理的日志")
            return True
        
        # 执行清理
        cleanup_result = mysql_service.cleanup_old_logs(retention_days)
        
        if cleanup_result.get('success'):
            print("✅ 日志清理完成!")
            print(f"   删除记录: {cleanup_result['deleted_count']:,} 条")
            print(f"   剩余记录: {cleanup_result['remaining_count']:,} 条")
            print(f"   清理时间: {cleanup_result['cleanup_time']}")
            
            # 显示清理后的统计
            print()
            print("📊 清理后统计:")
            new_retention_info = mysql_service.get_log_retention_info()
            if new_retention_info.get('success'):
                print(f"   总记录数: {new_retention_info['total_records']:,}")
                print(f"   30天内: {new_retention_info['retention_stats']['30天内']:,} 条")
        else:
            print(f"❌ 日志清理失败: {cleanup_result.get('message')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 清理日志失败: {e}")
        return False

def optimize_table():
    """优化日志表性能"""
    try:
        mysql_service = get_mysql_service()
        if not mysql_service.is_connected():
            print("❌ MySQL服务未连接")
            return False
        
        print("🔧 开始优化日志表性能...")
        print("=" * 50)
        
        # 显示优化前的表状态
        retention_info = mysql_service.get_log_retention_info()
        if retention_info.get('success'):
            print(f"📊 优化前状态:")
            print(f"   总记录数: {retention_info['total_records']:,}")
            print(f"   表大小: 约 {retention_info['total_records'] * 0.5 / 1024:.2f} MB (估算)")
        
        print()
        print("⏳ 正在优化表...")
        
        # 执行优化
        optimize_result = mysql_service.optimize_log_table()
        
        if optimize_result.get('success'):
            print("✅ 表优化完成!")
            print(f"   数据大小: {optimize_result['data_length_mb']} MB")
            print(f"   索引大小: {optimize_result['index_length_mb']} MB")
            print(f"   碎片空间: {optimize_result['fragmented_space_mb']} MB")
            print(f"   优化时间: {optimize_result.get('optimization_time', 'N/A')}")
        else:
            print(f"❌ 表优化失败: {optimimize_result.get('message')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 优化表失败: {e}")
        return False

def schedule_cleanup():
    """设置定时清理任务"""
    try:
        print("⏰ 设置定时清理任务")
        print("=" * 50)
        
        # 创建cron任务示例
        cron_example = f"""
# 每天凌晨2点清理超过30天的操作日志
0 2 * * * cd {project_root} && python scripts/maintain_logs.py --cleanup --retention-days 30 >> logs/log_maintenance.log 2>&1

# 每周日凌晨3点优化日志表
0 3 * * 0 cd {project_root} && python scripts/maintain_logs.py --optimize >> logs/log_maintenance.log 2>&1
"""
        
        print("📋 建议的cron任务配置:")
        print(cron_example)
        
        print("💡 使用方法:")
        print("   1. 编辑crontab: crontab -e")
        print("   2. 添加上面的任务配置")
        print("   3. 保存并退出")
        print("   4. 查看cron任务: crontab -l")
        
        return True
        
    except Exception as e:
        print(f"❌ 设置定时任务失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='操作日志维护工具')
    parser.add_argument('--stats', action='store_true', help='显示日志统计信息')
    parser.add_argument('--cleanup', action='store_true', help='清理过期日志')
    parser.add_argument('--optimize', action='store_true', help='优化日志表性能')
    parser.add_argument('--schedule', action='store_true', help='设置定时清理任务')
    parser.add_argument('--retention-days', type=int, default=30, help='日志保留天数 (默认: 30)')
    parser.add_argument('--force', action='store_true', help='强制清理 (即使没有过期日志)')
    
    args = parser.parse_args()
    
    # 如果没有指定参数，显示帮助信息
    if not any([args.stats, args.cleanup, args.optimize, args.schedule]):
        parser.print_help()
        return
    
    print("🚀 操作日志维护工具")
    print("=" * 50)
    
    success = True
    
    try:
        # 显示统计信息
        if args.stats:
            success &= show_log_stats()
            print()
        
        # 清理日志
        if args.cleanup:
            success &= cleanup_logs(args.retention_days, args.force)
            print()
        
        # 优化表
        if args.optimize:
            success &= optimize_table()
            print()
        
        # 设置定时任务
        if args.schedule:
            success &= schedule_cleanup()
            print()
        
        # 显示结果
        if success:
            print("🎉 所有操作完成!")
        else:
            print("❌ 部分操作失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
