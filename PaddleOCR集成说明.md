# PaddleOCR集成说明

## 概述

本项目已成功集成PaddleOCR作为可选的OCR识别引擎，与原有的Umi-OCR引擎形成双引擎架构。用户可以根据需要选择使用不同的OCR引擎。

## 功能特性

### 🚀 双引擎支持
- **Umi-OCR**: 原有的OCR引擎，支持多种语言模型
- **PaddleOCR**: 新增的OCR引擎，支持GPU加速

### 🔧 引擎选择
- 通过API参数灵活选择OCR引擎
- 支持引擎性能对比功能

### 📱 完整的Web界面
- 新增PaddleOCR专项测试页面
- 支持文件上传和Base64两种测试方式
- 提供引擎对比功能

## 安装依赖

```bash
pip install -r requirements.txt
```

新增的依赖项：
- `paddleocr`: PaddleOCR核心库
- `pillow`: 图像处理库
- `numpy`: 数值计算库

## API使用方法

### 1. 文件上传方式

```bash
curl -X POST "http://localhost:8000/ocr/recognize" \
  -F "file=@your_image.jpg" \
  -F "ocr.engine=paddleocr" \
  -F "paddleocr.device=gpu" \
  -F "data.format=text"
```

### 2. Base64方式

```bash
curl -X POST "http://localhost:8000/ocr/recognize/base64" \
  -H "Content-Type: application/json" \
  -d '{
    "base64": "your_base64_image_data",
    "options": {
      "ocr.engine": "paddleocr",
      "paddleocr.device": "gpu",
      "data.format": "text"
    }
  }'
```

## 参数说明

### 引擎选择参数
- `ocr.engine`: OCR引擎选择
  - `"umi_ocr"`: 使用Umi-OCR引擎（默认）
  - `"paddleocr"`: 使用PaddleOCR引擎

### PaddleOCR专用参数
- `paddleocr.device`: 计算设备选择
  - `"gpu"`: 使用GPU加速（推荐）
  - `"cpu"`: 使用CPU计算

### 通用参数
- `data.format`: 返回数据格式
  - `"dict"`: 返回详细的结构化数据
  - `"text"`: 返回纯文本

## Web测试界面

访问 `http://localhost:8000/test` 进入测试页面，包含以下功能：

### 📁 文件上传测试
- 支持选择图片文件进行OCR识别
- 可配置语言模型和返回格式

### 📝 Base64上传测试
- 支持直接输入Base64编码的图片数据
- 提供示例图片快速测试

### 🔧 PaddleOCR专项测试
- **文件识别**: 使用PaddleOCR识别上传的图片
- **Base64识别**: 使用PaddleOCR识别Base64图片
- **引擎对比**: 同时测试两个引擎，对比识别结果
- **设备选择**: 支持GPU/CPU设备切换

## 代码架构

### 新增文件

```
services/
├── paddleocr_service.py    # PaddleOCR服务封装类
models/
├── ocr_models.py         # 扩展的数据模型（增加引擎选择）
static/
├── test.html            # 更新的测试页面（新增PaddleOCR测试）
test_integration.py      # 集成测试脚本
```

### 核心类说明

#### PaddleOCRService
- `__init__(device)`: 初始化PaddleOCR服务
- `recognize_image(base64_image)`: 执行OCR识别
- `_decode_base64_image()`: Base64图片解码
- `_process_result()`: 处理OCR识别结果

#### 扩展的OCROptions
- `ocr_engine`: OCR引擎选择（新增）
- `paddleocr_device`: PaddleOCR设备选择（新增）

## 性能对比

### PaddleOCR优势
- ✅ GPU加速支持，识别速度快
- ✅ 支持多语言识别
- ✅ 开源免费，易于部署
- ✅ 模型轻量，资源占用少

### Umi-OCR优势
- ✅ 支持更多语言模型
- ✅ 排版解析能力强
- ✅ 配置选项丰富
- ✅ 生产环境稳定

## 使用建议

1. **速度优先**: 选择PaddleOCR + GPU
2. **精度优先**: 选择Umi-OCR + 适合的语言模型
3. **资源受限**: 选择PaddleOCR + CPU
4. **复杂排版**: 选择Umi-OCR + TBPU解析

## 故障排除

### PaddleOCR初始化失败
```bash
# 检查PaddlePaddle安装
pip install paddlepaddle-gpu  # GPU版本
# 或
pip install paddlepaddle      # CPU版本
```

### GPU不可用
- 检查CUDA环境配置
- 确认GPU驱动版本兼容性
- 可回退到CPU模式：`paddleocr.device=cpu`

### 内存不足
- 使用CPU模式减少内存占用
- 减小图片尺寸后再识别
- 调整PaddleOCR模型配置

## 测试验证

运行集成测试脚本验证安装：

```bash
python test_integration.py
```

测试内容包括：
- PaddleOCR库导入测试
- 服务模块导入测试
- 数据模型导入测试
- 服务初始化测试
- Base64解码测试

## 更新日志

### v1.1.0 (当前版本)
- ✅ 新增PaddleOCR引擎支持
- ✅ 实现双引擎架构
- ✅ 新增Web测试界面
- ✅ 支持引擎性能对比
- ✅ 完善错误处理机制

---

**注意**: 首次使用PaddleOCR时会自动下载模型文件，请确保网络连接正常。模型文件较大，下载可能需要几分钟时间。
