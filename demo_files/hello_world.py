#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World 演示程序
"""

def greet(name="世界"):
    """问候函数"""
    return f"你好，{name}！"

def calculate_sum(a, b):
    """计算两个数的和"""
    return a + b

if __name__ == "__main__":
    print(greet())
    print(f"1 + 2 = {calculate_sum(1, 2)}")
    
    # 循环示例
    for i in range(5):
        print(f"计数: {i}")
    
    print("演示完成！")
