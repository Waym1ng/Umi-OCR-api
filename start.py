#!/usr/bin/env python3
"""
OCR API服务启动脚本
"""

import os
import sys
import subprocess
import argparse

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)

def check_requirements():
    """检查依赖包是否安装"""
    try:
        import fastapi
        import uvicorn
        import requests
        import pydantic
        import python_multipart
        print("✓ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_ocr_service():
    """检查OCR服务是否运行"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:1224/api/ocr/get_options", timeout=5)
        if response.status_code == 200:
            print("✓ OCR服务运行正常")
            return True
        else:
            print(f"✗ OCR服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到OCR服务: {e}")
        print("请确保Umi-OCR服务在 http://127.0.0.1:1224 运行")
        return False

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        return False

def start_server(host="0.0.0.0", port=8000, reload=False):
    """启动API服务器"""
    print(f"启动OCR API服务...")
    print(f"服务地址: http://{host}:{port}")
    print(f"API文档: http://{host}:{port}/docs")
    print(f"健康检查: http://{host}:{port}/health")
    print("按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        import uvicorn
        
        # 配置uvicorn日志，减少噪音
        uvicorn_config = {
            "app": "main:app",
            "host": host,
            "port": port,
            "reload": reload,
            "log_level": "warning",  # 降低uvicorn的日志级别
            "access_log": False,     # 禁用访问日志
        }
        
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")

def main():
    parser = argparse.ArgumentParser(description="OCR API服务启动脚本")
    parser.add_argument("--host", default="0.0.0.0", help="服务器地址 (默认: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口 (默认: 8000)")
    parser.add_argument("--reload", action="store_true", help="启用热重载 (开发模式)")
    parser.add_argument("--install", action="store_true", help="安装依赖包")
    parser.add_argument("--skip-checks", action="store_true", help="跳过环境检查")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("OCR API服务启动脚本")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 安装依赖（如果指定）
    if args.install:
        if not install_requirements():
            sys.exit(1)
    
    # 环境检查
    if not args.skip_checks:
        print("执行环境检查...")
        
        # 检查依赖包
        if not check_requirements():
            if input("是否自动安装依赖包? (y/n): ").lower() == 'y':
                if not install_requirements():
                    sys.exit(1)
            else:
                sys.exit(1)
        
        # 检查OCR服务
        if not check_ocr_service():
            if input("OCR服务未运行，是否继续启动API服务? (y/n): ").lower() != 'y':
                sys.exit(1)
    
    print("-" * 50)
    
    # 启动服务器
    start_server(
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
