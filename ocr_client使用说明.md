# OCR客户端使用说明

这是一个用于调用OCR API的Python客户端工具，可以识别图片中的文字并返回纯文本结果。

## 功能特性

- 🖼️ 支持多种图片格式：jpg, jpeg, png, bmp, tiff, webp
- 🌐 调用 `/ocr/recognize/base64` 接口，返回纯文本格式
- 📝 自动将本地图片转换为base64编码
- ⚙️ 支持指定语言模型
- 📊 显示处理进度和耗时信息
- 💾 支持将结果保存到文件
- 🛡️ 完善的错误处理和用户提示
- 🔗 提供简洁的外部调用接口

## 安装依赖

确保已安装 `requests` 库：

```bash
pip install requests
```

## 使用方法

### 方式1：命令行使用

#### 基本用法

```bash
# 识别图片并输出到控制台
python ocr_client.py image.jpg
```

#### 指定API服务地址

```bash
# 使用本地服务
python ocr_client.py --url http://localhost:8000 image.png

# 使用指定IP地址
python ocr_client.py --url http://192.168.16.228:8000 photo.jpg
```

#### 指定语言模型

```bash
# 使用简体中文模型
python ocr_client.py --language models/config_chinese.txt document.jpg

# 使用英文模型
python ocr_client.py --language models/config_en.txt english_text.png
```

#### 保存结果到文件

```bash
# 保存识别结果到文本文件
python ocr_client.py --output result.txt image.jpg

# 同时指定语言模型和输出文件
python ocr_client.py --language models/config_chinese.txt --output result.txt scan.jpg
```

#### 完整参数示例

```bash
python ocr_client.py \
    --url http://192.168.16.228:8000 \
    --language models/config_chinese.txt \
    --output ocr_result.txt \
    /path/to/your/image.jpg
```

### 方式2：外部程序调用

#### 基本调用

```python
from ocr_client import recognize_image_text

# 基本用法 - 只需要图片路径
text_result = recognize_image_text("image.jpg")
print(text_result)
```

#### 指定API地址

```python
from ocr_client import recognize_image_text

# 使用自定义API地址
text_result = recognize_image_text("image.jpg", "http://localhost:8000")
print(text_result)
```

#### 在函数中使用

```python
from ocr_client import recognize_image_text

def process_document(image_path):
    """处理文档的函数"""
    try:
        text = recognize_image_text(image_path)
        lines = text.strip().split('\n')
        return {
            'success': True,
            'text': text,
            'lines_count': len(lines),
            'word_count': len(text.replace('\n', ''))
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# 使用函数
result = process_document("document.jpg")
if result['success']:
    print(f"识别成功，共{result['lines_count']}行，{result['word_count']}个字符")
else:
    print(f"识别失败：{result['error']}")
```

#### 批量处理

```python
from ocr_client import recognize_image_text

def batch_ocr(image_files):
    """批量OCR处理"""
    results = []
    for image_path in image_files:
        try:
            text = recognize_image_text(image_path)
            results.append({
                'file': image_path,
                'success': True,
                'text': text
            })
            print(f"✓ {image_path}: 识别成功")
        except Exception as e:
            results.append({
                'file': image_path,
                'success': False,
                'error': str(e)
            })
            print(f"✗ {image_path}: {e}")
    return results

# 使用示例
images = ["doc1.jpg", "doc2.png", "doc3.jpg"]
results = batch_ocr(images)
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `image_path` | 要识别的图片文件路径（必需） | - |
| `--url` | OCR API服务地址 | `http://192.168.16.228:8000` |
| `--language` | 语言模型路径（可选） | - |
| `--output`, `-o` | 输出文件路径（可选） | 输出到控制台 |
| `--help`, `-h` | 显示帮助信息 | - |

## 外部调用接口

### recognize_image_text 函数

```python
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
    """
```

#### 特性

- 🎯 **简单易用**：只需要传入图片路径即可
- 🔇 **静默模式**：不打印详细进度信息，适合程序调用
- 🎛️ **默认配置**：使用默认的API地址和text模式
- 🛡️ **异常处理**：保持原有的错误处理机制
- 📝 **返回纯文本**：直接返回识别结果

#### 使用场景

- 🔌 **集成到其他应用**
- 📦 **批量处理脚本**
- 🌐 **Web服务后端**
- 🤖 **自动化工作流**

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)
- WebP (.webp)

## 文件大小限制

- 最大支持：10MB
- 与API服务端限制保持一致

## 错误处理

客户端包含完善的错误处理机制：

- 📁 **文件不存在**：检查图片文件路径是否正确
- 🖼️ **格式不支持**：确认图片文件扩展名在支持列表中
- 📏 **文件过大**：图片文件大小超过10MB限制
- 🌐 **网络错误**：检查API服务地址和网络连接
- 🔧 **API错误**：显示详细的API错误信息

## 使用示例

### 示例1：命令行快速识别

```bash
$ python ocr_client.py test.jpg
正在处理图片: test.jpg
✓ 成功转换图片为base64，文件大小: 245678 bytes
正在请求OCR接口: http://192.168.16.228:8000/ocr/recognize/base64
✓ OCR识别成功，耗时: 1.23秒

==================================================
识别结果:
==================================================
这是一段测试文字
用于演示OCR客户端的功能
==================================================
```

### 示例2：外部程序调用

```python
from ocr_client import recognize_image_text

# 简单调用
try:
    text = recognize_image_text("invoice.jpg")
    print("识别结果:")
    print(text)
except Exception as e:
    print(f"识别失败: {e}")
```

### 示例3：批量处理脚本

```python
from ocr_client import recognize_image_text
import os

def process_folder(folder_path):
    """处理文件夹中的所有图片"""
    results = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            
            try:
                text = recognize_image_text(image_path)
                results.append((filename, text, None))
                print(f"✓ {filename}: 处理成功")
            except Exception as e:
                results.append((filename, None, str(e)))
                print(f"✗ {filename}: {e}")
    
    return results

# 使用示例
results = process_folder("./images")
for filename, text, error in results:
    if error:
        print(f"错误 {filename}: {error}")
    else:
        print(f"成功 {filename}: {len(text)} 字符")
```

## 技术细节

### API调用流程

1. 📁 读取本地图片文件
2. 🔄 转换为base64编码
3. 📦 构建JSON请求体
4. 🌐 发送POST请求到 `/ocr/recognize/base64`
5. 📝 接收纯文本响应
6. 📤 输出或保存结果

### 请求格式

```json
{
    "base64": "base64编码的图片数据",
    "options": {
        "data.format": "text"
    }
}
```

### 响应格式

成功时返回纯文本字符串，失败时返回错误信息。

## 故障排除

### 常见问题

1. **连接被拒绝**
   ```
   错误: 网络请求失败: HTTPConnectionPool(host='192.168.16.228', port=8000): Max retries exceeded with url: /ocr/recognize/base64 (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x...>: Failed to establish a new connection: [WinError 10061] 连接被拒绝'))
   ```
   **解决方案**：检查OCR服务是否正在运行，确认IP地址和端口是否正确。

2. **文件格式不支持**
   ```
   错误: 不支持的图片格式: .pdf。支持的格式: .jpg, .jpeg, .png, .bmp, .tiff, .webp
   ```
   **解决方案**：将PDF文件转换为图片格式后再进行识别。

3. **文件过大**
   ```
   错误: 文件过大: 15728640 bytes，最大允许: 10MB
   ```
   **解决方案**：压缩图片或裁剪图片尺寸后再进行识别。

## 开发者信息

- 客户端文件：`ocr_client.py`
- 示例文件：`ocr_example.py`
- 默认API地址：`http://192.168.16.228:8000`
- API接口：`/ocr/recognize/base64`
- 返回格式：纯文本（text模式）

## 文件结构

```
.
├── ocr_client.py          # 主客户端文件
├── ocr_example.py         # 外部调用示例
├── ocr_client使用说明.md   # 使用说明文档
└── static/
    └── test.html          # OCR测试页面
