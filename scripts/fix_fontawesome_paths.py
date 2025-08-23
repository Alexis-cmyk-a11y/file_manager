#!/usr/bin/env python3
# -*- coding: utf-8
"""
修复Font Awesome字体路径脚本
将CSS文件中的字体路径从../webfonts/改为../fonts/
"""

import os
import re

def fix_fontawesome_paths():
    """修复Font Awesome CSS文件中的字体路径"""
    print("🔧 修复Font Awesome字体路径...")
    
    css_file = "static/css/fontawesome-all.min.css"
    
    if not os.path.exists(css_file):
        print(f"❌ 找不到文件: {css_file}")
        return False
    
    try:
        # 读取CSS文件
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换字体路径
        # 将 ../webfonts/ 替换为 ../fonts/
        old_content = content
        content = re.sub(r'\.\./webfonts/', '../fonts/', content)
        
        # 检查是否有变化
        if old_content == content:
            print("   ℹ️  字体路径已经是正确的")
            return True
        
        # 写回文件
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ 字体路径已修复")
        return True
        
    except Exception as e:
        print(f"   ❌ 修复失败: {e}")
        return False

def verify_font_files():
    """验证字体文件是否存在"""
    print("\n🔍 验证字体文件...")
    
    font_files = [
        "static/fonts/fa-solid-900.woff2",
        "static/fonts/fa-solid-900.ttf",
        "static/fonts/fa-regular-400.woff2",
        "static/fonts/fa-regular-400.ttf",
        "static/fonts/fa-brands-400.woff2",
        "static/fonts/fa-brands-400.ttf"
    ]
    
    missing_files = []
    for font_file in font_files:
        if os.path.exists(font_file):
            size = os.path.getsize(font_file)
            print(f"   ✅ {font_file} ({size} bytes)")
        else:
            print(f"   ❌ {font_file} (缺失)")
            missing_files.append(font_file)
    
    if missing_files:
        print(f"\n⚠️  缺少以下字体文件:")
        for file in missing_files:
            print(f"      - {file}")
        print("   建议重新下载Font Awesome资源")
        return False
    
    return True

def download_missing_fonts():
    """下载缺失的字体文件"""
    print("\n📥 下载缺失的字体文件...")
    
    missing_fonts = [
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2", "static/fonts/fa-regular-400.woff2"),
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.ttf", "static/fonts/fa-regular-400.ttf"),
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2", "static/fonts/fa-brands-400.woff2"),
        ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.ttf", "static/fonts/fa-brands-400.ttf")
    ]
    
    import requests
    
    for url, local_path in missing_fonts:
        if not os.path.exists(local_path):
            try:
                print(f"   正在下载: {url}")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # 确保目录存在
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                # 写入文件
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"   ✅ 下载完成: {local_path}")
                
            except Exception as e:
                print(f"   ❌ 下载失败 {url}: {e}")
        else:
            print(f"   ℹ️  文件已存在: {local_path}")

def main():
    """主函数"""
    print("🚀 Font Awesome字体路径修复工具")
    print("=" * 50)
    
    # 修复CSS文件中的字体路径
    if fix_fontawesome_paths():
        print("✅ CSS文件路径修复完成")
    else:
        print("❌ CSS文件路径修复失败")
        return
    
    # 验证字体文件
    if verify_font_files():
        print("✅ 所有字体文件验证通过")
    else:
        print("⚠️  部分字体文件缺失")
        
        # 询问是否下载缺失的字体
        print("\n是否下载缺失的字体文件？(y/n): ", end="")
        try:
            choice = input().lower().strip()
            if choice in ['y', 'yes', '是', '']:
                download_missing_fonts()
            else:
                print("   跳过下载")
        except KeyboardInterrupt:
            print("\n   操作已取消")
    
    print("\n🎯 修复完成！现在图标应该可以正常显示了")
    print("💡 如果仍有问题，请检查浏览器开发者工具的网络面板")

if __name__ == "__main__":
    main()
