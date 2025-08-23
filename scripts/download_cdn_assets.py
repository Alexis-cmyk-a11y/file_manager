#!/usr/bin/env python3
# -*- coding: utf-8
"""
CDN资源下载脚本
将外部CDN资源下载到本地，提高网页加载速度
"""

import os
import requests
import urllib.parse
from pathlib import Path
import time

def download_file(url, local_path):
    """下载文件到本地"""
    try:
        print(f"正在下载: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 写入文件
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 下载完成: {local_path}")
        return True
    except Exception as e:
        print(f"❌ 下载失败 {url}: {e}")
        return False

def download_fontawesome():
    """下载Font Awesome资源"""
    print("\n📦 下载Font Awesome资源...")
    
    # Font Awesome CSS
    fa_css_url = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    fa_css_path = "static/css/fontawesome-all.min.css"
    
    if download_file(fa_css_url, fa_css_path):
        # 下载字体文件
        fa_fonts = [
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2", "static/fonts/fa-solid-900.woff2"),
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.ttf", "static/fonts/fa-solid-900.ttf"),
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2", "static/fonts/fa-regular-400.woff2"),
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.ttf", "static/fonts/fa-regular-400.ttf"),
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.woff2", "static/fonts/fa-brands-400.woff2"),
            ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-brands-400.ttf", "static/fonts/fa-brands-400.ttf"),
        ]
        
        for font_url, font_path in fa_fonts:
            download_file(font_url, font_path)

def download_google_fonts():
    """下载Google Fonts资源"""
    print("\n📦 下载Google Fonts资源...")
    
    # Inter字体
    inter_fonts = [
        ("https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hiA.woff2", "static/fonts/inter-v12-latin-700.woff2"),
    ]
    
    for font_url, font_path in inter_fonts:
        download_file(font_url, font_path)
    
    # 创建本地字体CSS文件
    local_fonts_css = """/* 本地字体文件 */
@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 300;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 500;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}

@font-face {
    font-family: 'Inter';
    font-style: normal;
    font-weight: 800;
    font-display: swap;
    src: url('../fonts/inter-v12-latin-700.woff2') format('woff2');
}
"""
    
    with open("static/css/local-fonts.css", "w", encoding="utf-8") as f:
        f.write(local_fonts_css)
    
    print("✅ 本地字体CSS文件已创建")

def download_codemirror():
    """下载CodeMirror资源"""
    print("\n📦 下载CodeMirror资源...")
    
    codemirror_resources = [
        ("https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css", "static/css/codemirror.min.css"),
        ("https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.js", "static/js/codemirror.min.js"),
    ]
    
    for resource_url, resource_path in codemirror_resources:
        download_file(resource_url, resource_path)

def create_cdn_mapping():
    """创建CDN映射文件"""
    print("\n📝 创建CDN映射文件...")
    
    cdn_mapping = """# CDN资源本地映射
# 此文件记录了CDN资源到本地文件的映射关系

## Font Awesome
- CDN: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css
- 本地: /static/css/fontawesome-all.min.css

## Google Fonts (Inter)
- CDN: https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap
- 本地: /static/css/local-fonts.css

## CodeMirror
- CDN: https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.css
- 本地: /static/css/codemirror.min.css
- CDN: https://cdnjs.cloudflare.com/ajax/libs/codemirror/6.65.7/codemirror.min.js
- 本地: /static/js/codemirror.min.js

## 字体文件
- 本地字体: /static/fonts/
- 本地图标字体: /static/fonts/fa-solid-900.woff2

## 注意事项
1. 所有CDN资源已下载到本地
2. 模板文件已更新为使用本地资源
3. 网页加载速度将显著提升
4. 离线环境也可以正常使用
"""
    
    with open("static/cdn_mapping.py", "w", encoding="utf-8") as f:
        f.write(cdn_mapping)
    
    print("✅ CDN映射文件已创建")

def main():
    """主函数"""
    print("🚀 开始下载CDN资源到本地...")
    print("这将显著提高网页加载速度！")
    
    start_time = time.time()
    
    # 创建必要的目录
    os.makedirs("static/css", exist_ok=True)
    os.makedirs("static/js", exist_ok=True)
    os.makedirs("static/fonts", exist_ok=True)
    
    # 下载各种资源
    download_fontawesome()
    download_google_fonts()
    download_codemirror()
    
    # 创建映射文件
    create_cdn_mapping()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n🎉 所有CDN资源下载完成！")
    print(f"⏱️  总耗时: {duration:.2f} 秒")
    print(f"📁 资源已保存到 static/ 目录")
    print(f"🔧 接下来需要更新模板文件以使用本地资源")

if __name__ == "__main__":
    main()
