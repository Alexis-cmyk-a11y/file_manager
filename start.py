#!/usr/bin/env python3
"""
文件管理系统启动脚本
提供更好的启动体验和错误处理
"""

import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        ('flask', 'flask'),
        ('werkzeug', 'werkzeug'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ 缺少必要的依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装依赖:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def create_env_file():
    """创建环境配置文件"""
    env_file = Path('.env')
    env_example = Path('env.example')
    
    if not env_file.exists() and env_example.exists():
        print("📝 创建环境配置文件...")
        try:
            with open(env_example, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(env_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            print("✅ 环境配置文件创建成功")
            print("💡 请根据需要修改 .env 文件中的配置")
            return True
        except Exception as e:
            print(f"❌ 创建环境配置文件失败: {e}")
            return False
    
    return True

def check_config():
    """检查配置文件"""
    config_file = Path('config.py')
    if not config_file.exists():
        print("❌ 配置文件 config.py 不存在")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def start_application():
    """启动应用程序"""
    print("🚀 启动文件管理系统...")
    
    try:
        # 导入并启动应用
        from app import app, Config
        
        print(f"📁 根目录: {Config.ROOT_DIR}")
        print(f"🌐 服务器地址: http://{Config.SERVER_HOST}:{Config.SERVER_PORT}")
        print(f"🔧 调试模式: {'开启' if Config.DEBUG_MODE else '关闭'}")
        print(f"🌍 环境: {Config.ENV}")
        
        # 延迟启动浏览器
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f"http://localhost:{Config.SERVER_PORT}")
            except Exception:
                pass
        
        # 在新线程中启动浏览器
        import threading
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        print("\n🎉 应用启动成功！")
        print("💡 浏览器将自动打开，如果没有自动打开，请手动访问上述地址")
        print("⏹️  按 Ctrl+C 停止应用")
        
        # 启动Flask应用
        app.run(
            debug=Config.DEBUG_MODE,
            host=Config.SERVER_HOST,
            port=Config.SERVER_PORT,
            use_reloader=False
        )
        
    except ImportError as e:
        print(f"❌ 导入应用失败: {e}")
        print("请确保所有依赖已正确安装")
        return False
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")
        return False

def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    try:
        result = subprocess.run([sys.executable, 'test_app.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 所有测试通过！")
            return True
        else:
            print("❌ 部分测试失败:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False

def show_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("📁 文件管理系统")
    print("="*50)
    print("1. 🚀 启动应用")
    print("2. 🧪 运行测试")
    print("3. 📋 检查环境")
    print("4. 📖 查看帮助")
    print("5. 🚪 退出")
    print("="*50)

def show_help():
    """显示帮助信息"""
    print("\n📖 帮助信息")
    print("-" * 30)
    print("这是一个基于Flask的文件管理系统，提供以下功能：")
    print("• 文件上传、下载、删除")
    print("• 文件夹创建、重命名")
    print("• 文件移动、复制")
    print("• 安全的文件类型验证")
    print("• 用户友好的Web界面")
    print("\n📁 配置文件:")
    print("• config.py - 主配置文件")
    print("• .env - 环境变量配置")
    print("\n🔧 启动方式:")
    print("• python start.py - 交互式启动")
    print("• python app.py - 直接启动")
    print("• python test_app.py - 运行测试")

def main():
    """主函数"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if not check_python_version():
        input("\n按回车键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        input("\n按回车键退出...")
        return
    
    # 检查配置
    if not check_config():
        input("\n按回车键退出...")
        return
    
    # 创建环境配置文件
    create_env_file()
    
    print("✅ 环境检查完成！")
    
    while True:
        show_menu()
        choice = input("请选择操作 (1-5): ").strip()
        
        if choice == '1':
            start_application()
            break
        elif choice == '2':
            run_tests()
            input("\n按回车键继续...")
        elif choice == '3':
            print("\n📋 环境检查结果:")
            print(f"✅ Python版本: {sys.version}")
            print(f"✅ 工作目录: {os.getcwd()}")
            print(f"✅ 配置文件: {'存在' if Path('config.py').exists() else '不存在'}")
            print(f"✅ 环境配置: {'存在' if Path('.env').exists() else '不存在'}")
            input("\n按回车键继续...")
        elif choice == '4':
            show_help()
            input("\n按回车键继续...")
        elif choice == '5':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  应用被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        input("\n按回车键退出...")
