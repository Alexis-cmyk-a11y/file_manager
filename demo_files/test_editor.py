#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编辑器功能的示例文件
"""

import os
import sys
from typing import List, Dict, Optional

class TestEditor:
    """测试编辑器类"""
    
    def __init__(self, name: str = "默认名称"):
        self.name = name
        self.items: List[str] = []
        self.config: Dict[str, any] = {}
    
    def add_item(self, item: str) -> bool:
        """添加项目"""
        if item and item not in self.items:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item: str) -> bool:
        """移除项目"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_items(self) -> List[str]:
        """获取所有项目"""
        return self.items.copy()
    
    def set_config(self, key: str, value: any) -> None:
        """设置配置"""
        self.config[key] = value
    
    def get_config(self, key: str, default: any = None) -> any:
        """获取配置"""
        return self.config.get(key, default)
    
    def process_data(self, data: List[str]) -> Dict[str, int]:
        """处理数据并返回统计信息"""
        result = {
            'total': len(data),
            'unique': len(set(data)),
            'empty': sum(1 for item in data if not item.strip())
        }
        return result

def main():
    """主函数"""
    print("测试编辑器功能")
    
    # 创建测试实例
    editor = TestEditor("Python编辑器测试")
    
    # 添加一些测试数据
    test_data = ["Python", "JavaScript", "HTML", "CSS", "SQL"]
    for item in test_data:
        editor.add_item(item)
    
    # 显示结果
    print(f"编辑器名称: {editor.name}")
    print(f"项目列表: {editor.get_items()}")
    
    # 测试数据处理
    stats = editor.process_data(test_data)
    print(f"统计信息: {stats}")
    
    # 测试配置
    editor.set_config('theme', 'dark')
    editor.set_config('font_size', 14)
    print(f"主题: {editor.get_config('theme')}")
    print(f"字体大小: {editor.get_config('font_size')}")

if __name__ == "__main__":
    main()
