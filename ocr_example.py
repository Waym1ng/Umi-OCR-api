#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR客户端外部调用示例
演示如何使用 recognize_image_text 函数进行简单的OCR识别
"""

from ocr_client import recognize_image_text


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 指定图片路径
    image_path = "merged_full_image_1764299014.png"  # 使用项目中现有的图片
    
    try:
        # 调用简洁的OCR函数
        text_result = recognize_image_text(image_path)
        
        print(f"识别成功！图片: {image_path}")
        print("识别结果:")
        print("-" * 50)
        print(text_result)
        print("-" * 50)
        
    except Exception as e:
        print(f"识别失败: {e}")


def example_with_custom_api():
    """使用自定义API地址的示例"""
    print("\n=== 自定义API地址示例 ===")
    
    image_path = "merged_full_image_1764299014.png"
    custom_api_url = "http://localhost:8000"  # 本地API地址
    
    try:
        # 使用自定义API地址
        text_result = recognize_image_text(image_path, custom_api_url)
        
        print(f"识别成功！使用API: {custom_api_url}")
        print("识别结果:")
        print("-" * 50)
        print(text_result)
        print("-" * 50)
        
    except Exception as e:
        print(f"识别失败: {e}")


def example_in_function():
    """在函数中使用OCR的示例"""
    print("\n=== 函数中使用示例 ===")
    
    def process_document(image_path):
        """处理文档的函数示例"""
        try:
            # 调用OCR识别
            text = recognize_image_text(image_path)
            
            # 简单的文本处理
            lines = text.strip().split('\n')
            word_count = len(text.replace('\n', '').replace(' ', ''))
            
            return {
                'success': True,
                'text': text,
                'lines_count': len(lines),
                'word_count': word_count,
                'preview': text[:100] + '...' if len(text) > 100 else text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # 使用函数
    image_path = "merged_full_image_1764299014.png"
    result = process_document(image_path)
    
    if result['success']:
        print("文档处理成功!")
        print(f"行数: {result['lines_count']}")
        print(f"字符数: {result['word_count']}")
        print(f"预览: {result['preview']}")
    else:
        print(f"文档处理失败: {result['error']}")


def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 模拟多个图片文件
    image_files = [
        "merged_full_image_1764299014.png",
        # 可以添加更多图片文件
    ]
    
    results = []
    
    for i, image_path in enumerate(image_files, 1):
        print(f"处理第 {i} 张图片: {image_path}")
        
        try:
            text = recognize_image_text(image_path)
            results.append({
                'file': image_path,
                'success': True,
                'text': text,
                'length': len(text)
            })
            print(f"✓ 成功识别，文本长度: {len(text)}")
            
        except Exception as e:
            results.append({
                'file': image_path,
                'success': False,
                'error': str(e)
            })
            print(f"✗ 识别失败: {e}")
    
    # 输出批量处理结果
    print(f"\n批量处理完成，共处理 {len(image_files)} 个文件")
    successful = sum(1 for r in results if r['success'])
    print(f"成功: {successful}，失败: {len(image_files) - successful}")
    
    for result in results:
        if result['success']:
            print(f"✓ {result['file']}: {result['length']} 字符")
        else:
            print(f"✗ {result['file']}: {result['error']}")


if __name__ == "__main__":
    """运行所有示例"""
    print("OCR客户端外部调用示例演示")
    print("=" * 60)
    
    # 运行各种示例
    example_basic_usage()
    example_with_custom_api()
    example_in_function()
    example_batch_processing()
    
    print("\n" + "=" * 60)
    print("示例演示完成!")
    print("\n使用说明:")
    print("1. 确保OCR服务正在运行")
    print("2. 确保图片文件存在")
    print("3. 根据需要修改API地址和图片路径")
