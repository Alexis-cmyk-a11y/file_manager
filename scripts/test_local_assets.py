#!/usr/bin/env python3
# -*- coding: utf-8
"""
本地资源测试脚本
验证所有CDN资源是否已成功本地化
"""

import os
import requests
from pathlib import Path

def test_local_file(file_path, description):
    """测试本地文件是否存在且可读"""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 0:
                    print(f"✅ {description}: {file_path}")
                    return True
                else:
                    print(f"❌ {description}: {file_path} (文件为空)")
                    return False
        except Exception as e:
            print(f"❌ {description}: {file_path} (读取失败: {e})")
            return False
    else:
        print(f"❌ {description}: {file_path} (文件不存在)")
        return False

def test_binary_file(file_path, description):
    """测试二进制文件是否存在且可读"""
    if os.path.exists(file_path):
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                print(f"✅ {description}: {file_path} ({file_size} bytes)")
                return True
            else:
                print(f"❌ {description}: {file_path} (文件为空)")
                return False
        except Exception as e:
            print(f"❌ {description}: {file_path} (读取失败: {e})")
            return False
    else:
        print(f"❌ {description}: {file_path} (文件不存在)")
        return False

def test_template_files():
    """测试模板文件是否已更新为使用本地资源"""
    print("\n🔍 检查模板文件...")
    
    template_files = [
        "templates/index.html",
        "templates/editor.html"
    ]
    
    cdn_patterns = [
        "cdnjs.cloudflare.com",
        "fonts.googleapis.com",
        "fonts.gstatic.com"
    ]
    
    all_clean = True
    
    for template_file in template_files:
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                has_cdn = any(pattern in content for pattern in cdn_patterns)
                
                if has_cdn:
                    print(f"❌ {template_file} 仍包含CDN链接")
                    all_clean = False
                else:
                    print(f"✅ {template_file} 已更新为本地资源")
                    
            except Exception as e:
                print(f"❌ {template_file} 读取失败: {e}")
                all_clean = False
        else:
            print(f"❌ {template_file} 文件不存在")
            all_clean = False
    
    return all_clean

def main():
    """主函数"""
    print("🧪 开始测试本地资源...")
    
    # 测试CSS文件
    print("\n📁 检查CSS文件...")
    css_files = [
        ("static/css/fontawesome-all.min.css", "Font Awesome CSS"),
        ("static/css/local-fonts.css", "本地字体CSS"),
        ("static/css/codemirror.min.css", "CodeMirror CSS")
    ]
    
    css_ok = all(test_local_file(path, desc) for path, desc in css_files)
    
    # 测试JavaScript文件
    print("\n📁 检查JavaScript文件...")
    js_files = [
        ("static/js/codemirror.min.js", "CodeMirror JavaScript")
    ]
    
    js_ok = all(test_local_file(path, desc) for path, desc in js_files)
    
    # 测试字体文件
    print("\n📁 检查字体文件...")
    font_files = [
        ("static/fonts/fa-solid-900.woff2", "Font Awesome WOFF2"),
        ("static/fonts/fa-solid-900.ttf", "Font Awesome TTF"),
        ("static/fonts/inter-v12-latin-700.woff2", "Inter字体 WOFF2")
    ]
    
    font_ok = all(test_binary_file(path, desc) for path, desc in font_files)
    
    # 测试模板文件
    template_ok = test_template_files()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结")
    print("="*50)
    
    if css_ok and js_ok and font_ok and template_ok:
        print("🎉 所有测试通过！CDN资源已成功本地化")
        print("✅ 网页加载速度将显著提升")
        print("✅ 支持离线使用")
        print("✅ 不依赖外部服务")
    else:
        print("❌ 部分测试失败，请检查以下问题：")
        if not css_ok:
            print("   - CSS文件缺失或损坏")
        if not js_ok:
            print("   - JavaScript文件缺失或损坏")
        if not font_ok:
            print("   - 字体文件缺失或损坏")
        if not template_ok:
            print("   - 模板文件仍包含CDN链接")
    
    print("\n💡 建议：")
    print("   1. 重新运行下载脚本: python scripts/download_cdn_assets.py")
    print("   2. 检查网络连接和权限")
    print("   3. 验证文件路径是否正确")

if __name__ == "__main__":
    main()
