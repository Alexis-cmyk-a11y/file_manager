#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理脚本
提供日志查看、清理、分析等功能
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger

class LogManager:
    """日志管理器"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.logger = get_logger('log_manager')
        
        if not self.log_dir.exists():
            self.logger.warning(f"日志目录不存在: {self.log_dir}")
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def list_log_files(self):
        """列出所有日志文件"""
        log_files = []
        
        for file_path in self.log_dir.rglob('*.log*'):
            if file_path.is_file():
                stat = file_path.stat()
                log_files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'size_mb': round(stat.st_size / (1024 * 1024), 2)
                })
        
        # 按修改时间排序
        log_files.sort(key=lambda x: x['modified'], reverse=True)
        return log_files
    
    def show_log_summary(self):
        """显示日志摘要信息"""
        log_files = self.list_log_files()
        
        if not log_files:
            print("📁 没有找到日志文件")
            return
        
        total_size = sum(f['size'] for f in log_files)
        total_files = len(log_files)
        
        print(f"📊 日志摘要 ({self.log_dir})")
        print(f"📁 总文件数: {total_files}")
        print(f"💾 总大小: {round(total_size / (1024 * 1024), 2)} MB")
        print()
        
        print("📋 日志文件列表:")
        for file_info in log_files:
            status = "🟢" if file_info['size'] < 10 * 1024 * 1024 else "🟡"  # 10MB
            if file_info['size'] > 100 * 1024 * 1024:  # 100MB
                status = "🔴"
            
            print(f"  {status} {file_info['name']}")
            print(f"     大小: {file_info['size_mb']} MB")
            print(f"     修改: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    def view_log_file(self, filename, lines=50, follow=False, filter_level=None):
        """查看日志文件内容"""
        file_path = self.log_dir / filename
        
        if not file_path.exists():
            print(f"❌ 日志文件不存在: {filename}")
            return
        
        print(f"📖 查看日志文件: {filename}")
        print(f"📍 路径: {file_path}")
        print(f"📏 大小: {round(file_path.stat().st_size / 1024, 2)} KB")
        print("-" * 80)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 读取最后几行
                all_lines = f.readlines()
                start_line = max(0, len(all_lines) - lines)
                
                for i, line in enumerate(all_lines[start_line:], start_line + 1):
                    if self._should_display_line(line, filter_level):
                        print(f"{i:6d}: {line.rstrip()}")
                
                if follow:
                    print("\n🔄 实时监控模式 (按 Ctrl+C 停止)")
                    try:
                        while True:
                            new_lines = f.readlines()
                            for line in new_lines:
                                if self._should_display_line(line, filter_level):
                                    print(f"NEW: {line.rstrip()}")
                    except KeyboardInterrupt:
                        print("\n⏹️  停止监控")
        
        except Exception as e:
            print(f"❌ 读取日志文件失败: {e}")
    
    def _should_display_line(self, line, filter_level):
        """判断是否应该显示该行"""
        if not filter_level:
            return True
        
        # 尝试解析JSON格式的日志
        try:
            log_data = json.loads(line.strip())
            if 'level' in log_data:
                return log_data['level'].upper() == filter_level.upper()
        except:
            pass
        
        # 传统格式日志
        level_pattern = rf'\b{filter_level.upper()}\b'
        return re.search(level_pattern, line, re.IGNORECASE) is not None
    
    def search_logs(self, query, files=None, case_sensitive=False):
        """搜索日志内容"""
        if files is None:
            files = [f.name for f in self.log_dir.glob('*.log')]
        
        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for filename in files:
            file_path = self.log_dir / filename
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if re.search(query, line, flags):
                            results.append({
                                'file': filename,
                                'line': line_num,
                                'content': line.strip(),
                                'timestamp': self._extract_timestamp(line)
                            })
            except Exception as e:
                print(f"⚠️  读取文件 {filename} 失败: {e}")
        
        # 按时间排序
        results.sort(key=lambda x: x['timestamp'] or datetime.min)
        
        print(f"🔍 搜索结果: '{query}'")
        print(f"📊 找到 {len(results)} 条匹配记录")
        print("-" * 80)
        
        for result in results:
            print(f"📄 {result['file']}:{result['line']}")
            print(f"⏰ {result['timestamp'] or 'Unknown'}")
            print(f"📝 {result['content']}")
            print("-" * 40)
    
    def _extract_timestamp(self, line):
        """从日志行中提取时间戳"""
        # JSON格式
        try:
            log_data = json.loads(line.strip())
            if 'timestamp' in log_data:
                return datetime.fromisoformat(log_data['timestamp'].replace('Z', '+00:00'))
        except:
            pass
        
        # 传统格式
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    return datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                except:
                    try:
                        return datetime.fromisoformat(match.group(1))
                    except:
                        pass
        
        return None
    
    def clean_old_logs(self, days=30, dry_run=True):
        """清理旧日志文件"""
        cutoff_date = datetime.now() - timedelta(days=days)
        old_files = []
        
        for file_path in self.log_dir.rglob('*.log*'):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    old_files.append({
                        'path': file_path,
                        'size': file_path.stat().st_size,
                        'modified': mtime
                    })
        
        if not old_files:
            print("✨ 没有需要清理的旧日志文件")
            return
        
        total_size = sum(f['size'] for f in old_files)
        print(f"🗑️  找到 {len(old_files)} 个旧日志文件")
        print(f"💾 总大小: {round(total_size / (1024 * 1024), 2)} MB")
        print(f"📅 清理 {days} 天前的文件")
        print()
        
        for file_info in old_files:
            print(f"  📄 {file_info['path'].name}")
            print(f"     大小: {round(file_info['size'] / 1024, 2)} KB")
            print(f"     修改: {file_info['modified'].strftime('%Y-%m-%d')}")
        
        if not dry_run:
            print(f"\n🗑️  正在删除 {len(old_files)} 个文件...")
            for file_info in old_files:
                try:
                    file_info['path'].unlink()
                    print(f"  ✅ 已删除: {file_info['path'].name}")
                except Exception as e:
                    print(f"  ❌ 删除失败: {file_info['path'].name} - {e}")
            
            print(f"\n✨ 清理完成，释放空间: {round(total_size / (1024 * 1024), 2)} MB")
        else:
            print(f"\n🔍 这是预览模式，使用 --execute 参数执行实际清理")
    
    def analyze_logs(self, filename, hours=24):
        """分析日志文件"""
        file_path = self.log_dir / filename
        
        if not file_path.exists():
            print(f"❌ 日志文件不存在: {filename}")
            return
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 统计信息
        stats = {
            'total_lines': 0,
            'level_counts': {},
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0,
            'debug_count': 0,
            'time_distribution': {},
            'top_errors': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    stats['total_lines'] += 1
                    
                    # 解析日志级别
                    level = self._extract_log_level(line)
                    if level:
                        stats['level_counts'][level] = stats['level_counts'].get(level, 0) + 1
                        
                        if level == 'ERROR':
                            stats['error_count'] += 1
                        elif level == 'WARNING':
                            stats['warning_count'] += 1
                        elif level == 'INFO':
                            stats['info_count'] += 1
                        elif level == 'DEBUG':
                            stats['debug_count'] += 1
                    
                    # 时间分布
                    timestamp = self._extract_timestamp(line)
                    if timestamp and timestamp >= cutoff_time:
                        hour = timestamp.strftime('%Y-%m-%d %H:00')
                        stats['time_distribution'][hour] = stats['time_distribution'].get(hour, 0) + 1
                    
                    # 收集错误信息
                    if level == 'ERROR':
                        error_msg = self._extract_error_message(line)
                        if error_msg:
                            stats['top_errors'].append(error_msg)
        
        except Exception as e:
            print(f"❌ 分析日志文件失败: {e}")
            return
        
        # 显示分析结果
        print(f"📊 日志分析报告: {filename}")
        print(f"⏰ 分析时间范围: 最近 {hours} 小时")
        print(f"📏 总行数: {stats['total_lines']}")
        print()
        
        print("📈 日志级别统计:")
        for level, count in sorted(stats['level_counts'].items()):
            percentage = (count / stats['total_lines']) * 100
            print(f"  {level}: {count} ({percentage:.1f}%)")
        print()
        
        print("⏰ 时间分布 (最近24小时):")
        for hour, count in sorted(stats['time_distribution'].items()):
            print(f"  {hour}: {count} 条")
        print()
        
        if stats['top_errors']:
            print("🚨 常见错误 (前10个):")
            error_counts = {}
            for error in stats['top_errors']:
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {count}x: {error}")
    
    def _extract_log_level(self, line):
        """从日志行中提取日志级别"""
        # JSON格式
        try:
            log_data = json.loads(line.strip())
            if 'level' in log_data:
                return log_data['level'].upper()
        except:
            pass
        
        # 传统格式
        level_pattern = r'\b(DEBUG|INFO|WARNING|ERROR|CRITICAL)\b'
        match = re.search(level_pattern, line, re.IGNORECASE)
        return match.group(1).upper() if match else None
    
    def _extract_error_message(self, line):
        """从日志行中提取错误消息"""
        # JSON格式
        try:
            log_data = json.loads(line.strip())
            if 'message' in log_data:
                return log_data['message'][:100]  # 限制长度
        except:
            pass
        
        # 传统格式
        return line.strip()[:100]

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='日志管理工具')
    parser.add_argument('--log-dir', default='logs', help='日志目录路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出日志文件
    subparsers.add_parser('list', help='列出所有日志文件')
    
    # 查看日志文件
    view_parser = subparsers.add_parser('view', help='查看日志文件内容')
    view_parser.add_argument('filename', help='日志文件名')
    view_parser.add_argument('-n', '--lines', type=int, default=50, help='显示行数')
    view_parser.add_argument('-f', '--follow', action='store_true', help='实时监控')
    view_parser.add_argument('--level', help='过滤日志级别')
    
    # 搜索日志
    search_parser = subparsers.add_parser('search', help='搜索日志内容')
    search_parser.add_argument('query', help='搜索查询')
    search_parser.add_argument('--files', nargs='+', help='指定日志文件')
    search_parser.add_argument('--case-sensitive', action='store_true', help='区分大小写')
    
    # 清理旧日志
    clean_parser = subparsers.add_parser('clean', help='清理旧日志文件')
    clean_parser.add_argument('--days', type=int, default=30, help='保留天数')
    clean_parser.add_argument('--execute', action='store_true', help='执行实际清理')
    
    # 分析日志
    analyze_parser = subparsers.add_parser('analyze', help='分析日志文件')
    analyze_parser.add_argument('filename', help='日志文件名')
    analyze_parser.add_argument('--hours', type=int, default=24, help='分析时间范围(小时)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建日志管理器
    log_manager = LogManager(args.log_dir)
    
    # 执行命令
    if args.command == 'list':
        log_manager.show_log_summary()
    elif args.command == 'view':
        log_manager.view_log_file(args.filename, args.lines, args.follow, args.level)
    elif args.command == 'search':
        log_manager.search_logs(args.query, args.files, args.case_sensitive)
    elif args.command == 'clean':
        log_manager.clean_old_logs(args.days, not args.execute)
    elif args.command == 'analyze':
        log_manager.analyze_logs(args.filename, args.hours)

if __name__ == '__main__':
    main()
