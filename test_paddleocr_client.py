#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddleOCR客户端测试脚本
用于验证paddleocr_client.py的基本功能
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_import():
    """测试模块导入"""
    try:
        from paddleocr_client import PaddleOCRClient, recognize_image_text
        logger.info("✅ PaddleOCR客户端模块导入成功")
        return True
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False

def test_client_init():
    """测试客户端初始化"""
    try:
        from paddleocr_client import PaddleOCRClient
        
        # 测试默认初始化
        client1 = PaddleOCRClient()
        logger.info(f"✅ 默认初始化成功: {client1.api_url}, 设备: {client1.device}")
        
        # 测试自定义初始化
        client2 = PaddleOCRClient("http://localhost:8000", "cpu")
        logger.info(f"✅ 自定义初始化成功: {client2.api_url}, 设备: {client2.device}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 客户端初始化失败: {e}")
        return False

def test_base64_conversion():
    """测试Base64转换功能"""
    try:
        from paddleocr_client import PaddleOCRClient
        
        # 创建一个测试用的简单base64字符串（1x1像素红色点）
        test_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        
        # 保存为临时文件进行测试
        import tempfile
        import base64
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(base64.b64decode(test_base64))
            tmp_path = tmp_file.name
        
        try:
            client = PaddleOCRClient()
            result = client.image_to_base64(tmp_path)
            
            # 验证base64结果（去掉可能的换行符）
            if result.replace('\n', '').replace('\r', '') == test_base64:
                logger.info("✅ Base64转换测试成功")
                return True
            else:
                logger.error(f"❌ Base64转换结果不匹配")
                return False
                
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"❌ Base64转换测试失败: {e}")
        return False

def test_convenience_function():
    """测试便捷函数"""
    try:
        from paddleocr_client import recognize_image_text
        
        # 创建一个测试用的简单base64字符串
        test_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        
        # 保存为临时文件进行测试
        import tempfile
        import base64
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(base64.b64decode(test_base64))
            tmp_path = tmp_file.name
        
        try:
            # 测试便捷函数
            try:
                result = recognize_image_text(tmp_path)
                logger.info("✅ 便捷函数调用成功（API服务可用）")
                return True
            except Exception as api_error:
                if "PaddleOCR识别失败" in str(api_error) or "网络请求失败" in str(api_error):
                    logger.info("✅ 便捷函数调用正常（API服务未运行，符合预期）")
                    return True
                else:
                    logger.error(f"❌ 便捷函数异常: {api_error}")
                    return False
                
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"❌ 便捷函数测试失败: {e}")
        return False

def test_command_line_interface():
    """测试命令行接口"""
    try:
        import subprocess
        import tempfile
        import base64
        
        # 创建测试图片
        test_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_file.write(base64.b64decode(test_base64))
            tmp_path = tmp_file.name
        
        try:
            # 测试帮助信息
            result = subprocess.run([
                sys.executable, 'paddleocr_client.py', '--help'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'PaddleOCR客户端' in result.stdout:
                logger.info("✅ 命令行接口测试成功")
                return True
            else:
                logger.error(f"❌ 命令行接口异常: {result.stderr}")
                return False
                
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"❌ 命令行接口测试失败: {e}")
        return False

def main():
    """主测试函数"""
    logger.info("🧪 开始PaddleOCR客户端测试")
    logger.info("=" * 50)
    
    tests = [
        ("模块导入测试", test_import),
        ("客户端初始化测试", test_client_init),
        ("Base64转换测试", test_base64_conversion),
        ("便捷函数测试", test_convenience_function),
        ("命令行接口测试", test_command_line_interface),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n🔧 执行测试: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                logger.warning(f"⚠️ 测试失败: {test_name}")
        except Exception as e:
            logger.error(f"💥 测试异常: {test_name} - {e}")
    
    logger.info("\n" + "=" * 50)
    logger.info(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！PaddleOCR客户端准备就绪")
        return 0
    else:
        logger.error("❌ 部分测试失败，请检查代码实现")
        return 1

if __name__ == "__main__":
    sys.exit(main())
