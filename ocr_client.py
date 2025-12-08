#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR客户端 - 调用OCR API识别图片文字
使用/ocr/recognize/base64接口，返回纯文本结果
"""

import base64
import requests
import json
import sys
import os
import argparse
from pathlib import Path
from typing import Optional


class OCRClient:
    """OCR客户端类"""
    
    def __init__(self, api_url: str = "http://192.168.16.228:8000"):
        """
        初始化OCR客户端
        
        Args:
            api_url: OCR API服务地址
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        # 设置请求超时时间
        self.session.timeout = 30
    
    def image_to_base64(self, image_path: str) -> str:
        """
        将本地图片文件转换为base64编码字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: base64编码字符串（不含前缀）
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或文件损坏
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 检查文件格式
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        file_ext = Path(image_path).suffix.lower()
        if file_ext not in allowed_extensions:
            raise ValueError(f"不支持的图片格式: {file_ext}。支持的格式: {', '.join(allowed_extensions)}")
        
        try:
            # 读取图片文件并转换为base64
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 检查文件大小（限制为10MB，与API服务端一致）
            if len(image_bytes) > 10 * 1024 * 1024:
                raise ValueError(f"文件过大: {len(image_bytes)} bytes，最大允许: 10MB")
            
            # 转换为base64
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            
            print(f"✓ 成功转换图片为base64，文件大小: {len(image_bytes)} bytes")
            return base64_str
            
        except Exception as e:
            raise ValueError(f"图片处理失败: {str(e)}")
    
    def _image_to_base64_silent(self, image_path: str) -> str:
        """
        将本地图片文件转换为base64编码字符串（静默版本）
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: base64编码字符串（不含前缀）
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持或文件损坏
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 检查文件格式
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        file_ext = Path(image_path).suffix.lower()
        if file_ext not in allowed_extensions:
            raise ValueError(f"不支持的图片格式: {file_ext}。支持的格式: {', '.join(allowed_extensions)}")
        
        try:
            # 读取图片文件并转换为base64
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # 检查文件大小（限制为10MB，与API服务端一致）
            if len(image_bytes) > 10 * 1024 * 1024:
                raise ValueError(f"文件过大: {len(image_bytes)} bytes，最大允许: 10MB")
            
            # 转换为base64
            base64_str = base64.b64encode(image_bytes).decode('utf-8')
            
            return base64_str
            
        except Exception as e:
            raise ValueError(f"图片处理失败: {str(e)}")
    
    def recognize_text(self, image_path: str, language: Optional[str] = None, verbose: bool = True) -> str:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            language: 语言模型（可选）
            verbose: 是否显示详细进度信息（默认True）
            
        Returns:
            str: 识别的文字结果（纯文本）
            
        Raises:
            Exception: OCR识别失败
        """
        try:
            # 转换图片为base64
            if verbose:
                print(f"正在处理图片: {image_path}")
            base64_image = self._image_to_base64_silent(image_path)
            
            # 构建请求数据
            request_data = {
                "base64": base64_image,
                "options": {
                    "data.format": "text"  # 指定返回纯文本格式
                }
            }
            
            # 如果指定了语言模型，添加到选项中
            if language:
                request_data["options"]["ocr.language"] = language
                if verbose:
                    print(f"使用语言模型: {language}")
            
            # 发送请求
            api_endpoint = f"{self.api_url}/ocr/recognize/base64"
            if verbose:
                print(f"正在请求OCR接口: {api_endpoint}")
            
            response = self.session.post(
                api_endpoint,
                json=request_data,
                headers={'Content-Type': 'application/json'}
            )
            
            # 检查响应状态
            if response.status_code == 200:
                # text模式下直接返回纯文本
                text_result = response.text
                if verbose:
                    print(f"✓ OCR识别成功，耗时: {response.elapsed.total_seconds():.2f}秒")
                return text_result
            else:
                # 尝试解析错误信息
                try:
                    error_info = response.json()
                    error_msg = error_info.get('detail', f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                
                raise Exception(f"OCR识别失败: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise Exception(f"OCR处理异常: {str(e)}")


def recognize_image_text(image_path: str, api_url: str = "http://192.168.16.228:8000") -> str:
    """
    简单的OCR文字识别函数，方便外部调用
    
    Args:
        image_path: 图片文件路径
        api_url: OCR API服务地址（可选，使用默认值）
        
    Returns:
        str: 识别的文字结果
        
    Raises:
        Exception: OCR识别失败
        
    Example:
        >>> # 外部程序调用示例
        >>> from ocr_client import recognize_image_text
        >>> text = recognize_image_text("image.jpg")
        >>> print(text)
        
        >>> # 指定API地址
        >>> text = recognize_image_text("image.jpg", "http://localhost:8000")
    """
    try:
        # 创建OCR客户端实例
        client = OCRClient(api_url)
        
        # 调用静默模式进行识别
        result = client.recognize_text(image_path, verbose=False)
        
        return result
        
    except Exception as e:
        # 重新抛出异常，让调用者处理
        raise Exception(f"OCR识别失败: {str(e)}")


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="OCR客户端 - 识别图片中的文字",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python ocr_client.py image.jpg
  python ocr_client.py --url http://localhost:8000 image.png
  python ocr_client.py --language models/config_chinese.txt photo.jpg
        """
    )
    
    parser.add_argument(
        'image_path',
        help='要识别的图片文件路径'
    )
    
    parser.add_argument(
        '--url',
        default='http://192.168.16.228:8000',
        help='OCR API服务地址 (默认: http://192.168.16.228:8000)'
    )
    
    parser.add_argument(
        '--language',
        help='语言模型路径 (可选，如: models/config_chinese.txt)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出文件路径 (可选，默认输出到控制台)'
    )
    
    args = parser.parse_args()
    
    try:
        # 创建OCR客户端
        client = OCRClient(args.url)
        
        # 执行OCR识别
        result = client.recognize_text(args.image_path, args.language)
        
        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✓ 识别结果已保存到: {args.output}")
        else:
            print("\n" + "="*50)
            print("识别结果:")
            print("="*50)
            print(result)
            print("="*50)
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
