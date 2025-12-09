# Umi-OCR API 服务

基于 FastAPI 的 OCR 文字识别服务，提供简洁易用的 REST API 接口，支持多种图片格式的文字识别。现已集成 PaddleOCR 引擎，支持双引擎架构。

## ✨ 功能特性

- 🚀 **双引擎支持**：支持 Umi-OCR 和 PaddleOCR 两种识别引擎
- 🖼️ **多格式支持**：支持 JPG、PNG、BMP、TIFF、WebP 等图片格式
- 🌐 **RESTful API**：提供标准的 REST API 接口，易于集成
- 📝 **多种数据格式**：支持返回详细字典格式或纯文本格式
- 🛡️ **完善的错误处理**：详细的错误信息和异常处理机制
- 📊 **实时日志**：完整的请求处理日志记录
- 🔧 **灵活配置**：支持多种 OCR 参数配置和引擎选择
- 📱 **Web 测试界面**：内置测试页面，支持引擎对比测试
- 🧩 **Python 客户端**：提供独立的 Python 客户端工具
- ⚡ **GPU 加速**：PaddleOCR 引擎支持 GPU 加速识别

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Umi-OCR 服务（默认运行在 http://127.0.0.1:1224）
- CUDA 环境（可选，用于 PaddleOCR GPU 加速）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**依赖包说明：**
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `python-multipart` - 文件上传支持
- `requests` - HTTP 客户端
- `pydantic` - 数据验证
- `paddleocr` - PaddleOCR 引擎库
- `pillow` - 图像处理库
- `numpy` - 数值计算库

**PaddleOCR 可选依赖：**
```bash
# GPU 版本（推荐）
pip install paddlepaddle-gpu

# CPU 版本
pip install paddlepaddle
```

### 2. 启动服务

#### 方式1：使用启动脚本（推荐）
```bash
python start.py
```

#### 方式2：直接启动
```bash
python main.py
```

服务启动后将在以下端口运行：
- **API 服务**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **测试页面**：http://localhost:8000/test

### 3. 验证服务

打开浏览器访问：
- 测试页面：http://localhost:8000/test.html
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 📋 项目结构

```
Umi-OCR-api/
├── main.py                     # FastAPI 主应用文件
├── start.py                    # 启动脚本，包含环境检查
├── ocr_client.py              # Umi-OCR Python 客户端工具
├── ocr_example.py             # 客户端使用示例
├── ocr_client使用说明.md        # 客户端详细使用说明
├── paddleocr_client.py         # PaddleOCR Python 客户端工具
├── paddleocr_example.py        # PaddleOCR 使用示例
├── PaddleOCR集成说明.md        # PaddleOCR 集成详细说明
├── test_integration.py         # 集成功能测试脚本
├── test_paddleocr_client.py   # PaddleOCR 客户端测试脚本
├── Umi-api文档.md              # 原始 API 文档参考
├── requirements.txt            # Python 依赖包列表
├── README.md                  # 项目文档
├── .gitignore                 # Git 忽略文件
├── models/
│   └── ocr_models.py          # Pydantic 数据模型（支持双引擎）
├── services/
│   ├── ocr_service.py         # OCR 服务调用逻辑（支持多引擎）
│   └── paddleocr_service.py    # PaddleOCR 服务封装
├── utils/
│   └── image_utils.py         # 图片处理工具
└── static/
    └── test.html              # Web 测试页面（支持引擎对比）
```

## 🔧 API 接口详解

### 核心接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/ocr/recognize` | 文件上传识别 |
| POST | `/ocr/recognize/base64` | Base64 图片识别 |
| GET | `/ocr/options` | 获取 OCR 参数选项 |
| GET | `/health` | 健康检查 |
| GET | `/docs` | Swagger API 文档 |
| GET | `/test` | 重定向到测试页面 |

### 1. 文件上传识别

**接口：** `POST /ocr/recognize`

**请求参数：**
- `file` (File): 图片文件（必需）
- `ocr.engine` (str): OCR引擎选择，umi_ocr/paddleocr（可选，默认umi_ocr）
- `ocr.language` (str): 语言模型（可选，仅Umi-OCR引擎）
- `ocr.cls` (bool): 纠正文本方向（可选，仅Umi-OCR引擎）
- `ocr.limit_side_len` (int): 限制图像边长（可选，仅Umi-OCR引擎）
- `tbpu.parser` (str): 排版解析方案（可选，仅Umi-OCR引擎）
- `paddleocr.device` (str): PaddleOCR设备类型，gpu/cpu（可选，仅PaddleOCR引擎）
- `data.format` (str): 返回格式，dict/text（可选）

**示例：**
```bash
# 使用默认Umi-OCR引擎
curl -X POST "http://localhost:8000/ocr/recognize" \
  -F "file=@test.jpg" \
  -F "data.format=text"

# 使用PaddleOCR引擎（GPU）
curl -X POST "http://localhost:8000/ocr/recognize" \
  -F "file=@test.jpg" \
  -F "ocr.engine=paddleocr" \
  -F "paddleocr.device=gpu" \
  -F "data.format=text"

# 使用PaddleOCR引擎（CPU）
curl -X POST "http://localhost:8000/ocr/recognize" \
  -F "file=@test.jpg" \
  -F "ocr.engine=paddleocr" \
  -F "paddleocr.device=cpu" \
  -F "data.format=text"
```

### 2. Base64 图片识别

**接口：** `POST /ocr/recognize/base64`

**请求体：**
```json
{
    "base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "options": {
        "data.format": "text",
        "ocr.language": "models/config_chinese.txt"
    }
}
```

**示例：**
```bash
curl -X POST "http://localhost:8000/ocr/recognize/base64" \
  -H "Content-Type: application/json" \
  -d '{
    "base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "options": {
      "data.format": "text"
    }
  }'
```

### 3. 获取参数选项

**接口：** `GET /ocr/options`

返回所有可用的 OCR 参数定义、默认值、可选值等信息。

**示例：**
```bash
curl "http://localhost:8000/ocr/options"
```

## 🧪 测试方法

### 1. Web 测试页面

1. 启动服务后，访问 http://localhost:8000/test.html
2. 页面会自动检查服务状态
3. 选择"文件上传"或"Base64上传"标签页
4. 上传图片或输入 base64 数据进行测试
5. 查看识别结果和详细信息

### 2. Python 客户端测试

项目提供了独立的 Python 客户端工具，支持双引擎：

#### Umi-OCR 客户端
```bash
# 识别图片并输出到控制台
python ocr_client.py image.jpg

# 指定 API 服务地址
python ocr_client.py --url http://localhost:8000 image.png

# 保存结果到文件
python ocr_client.py --output result.txt image.jpg
```

#### PaddleOCR 客户端
```bash
# 使用 PaddleOCR 识别图片（默认GPU）
python paddleocr_client.py image.jpg

# 使用 CPU 模式
python paddleocr_client.py --device cpu image.jpg

# 批量处理
python paddleocr_client.py --batch *.jpg --output results.txt

# 保存结果到文件
python paddleocr_client.py --output result.txt image.jpg
```

#### 编程调用

**Umi-OCR：**
```python
from ocr_client import recognize_image_text

# 基本用法
text_result = recognize_image_text("image.jpg")
print(text_result)

# 使用自定义 API 地址
text_result = recognize_image_text("image.jpg", "http://localhost:8000")
```

**PaddleOCR：**
```python
from paddleocr_client import recognize_image_text

# 基本用法（默认GPU）
text_result = recognize_image_text("image.jpg")
print(text_result)

# 使用自定义 API 地址和设备
text_result = recognize_image_text("image.jpg", "http://localhost:8000", "cpu")
print(text_result)
```

### 3. 健康检查

```bash
curl "http://localhost:8000/health"
```

正常响应：
```json
{
    "status": "healthy",
    "ocr_service": "connected"
}
```

## ⚙️ 配置说明

### CORS 配置

当前允许所有源访问，生产环境建议修改：

```python
# 在 main.py 中修改
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-domain.com"],  # 修改为具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### OCR 服务地址

默认地址：`http://127.0.0.1:1224/api/ocr`

如需修改，编辑 `services/ocr_service.py` 中的 `ocr_url` 参数。

### 支持的 OCR 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `ocr.engine` | `umi_ocr` | OCR引擎选择（umi_ocr/paddleocr） |
| `ocr.language` | `models/config_chinese.txt` | 语言/模型库（仅Umi-OCR引擎） |
| `ocr.cls` | `false` | 纠正文本方向（仅Umi-OCR引擎） |
| `ocr.limit_side_len` | `960` | 限制图像边长（仅Umi-OCR引擎） |
| `tbpu.parser` | `multi_para` | 排版解析方案（仅Umi-OCR引擎） |
| `tbpu.ignoreArea` | `[]` | 忽略区域（仅Umi-OCR引擎） |
| `paddleocr.device` | `gpu` | PaddleOCR设备类型（仅PaddleOCR引擎） |
| `data.format` | `dict` | 数据返回格式 |

### 引擎选择建议

| 场景 | 推荐引擎 | 配置 |
|------|--------|------|
| 速度优先 | PaddleOCR | `ocr.engine=paddleocr`, `paddleocr.device=gpu` |
| 精度优先 | Umi-OCR | `ocr.engine=umi_ocr`, 适合的语言模型 |
| 资源受限 | PaddleOCR | `ocr.engine=paddleocr`, `paddleocr.device=cpu` |
| 复杂排版 | Umi-OCR | `ocr.engine=umi_ocr`, `tbpu.parser=multi_para` |

## 🔍 故障排除

### 常见问题及解决方案

#### 1. 服务启动失败

**可能原因：**
- Python 版本不兼容（需要 3.8+）
- 依赖包未安装
- 端口 8000 被占用

**解决方案：**
```bash
# 检查 Python 版本
python --version

# 安装依赖
pip install -r requirements.txt

# 检查端口占用
netstat -ano | findstr :8000
```

#### 2. OCR 连接失败

**可能原因：**
- Umi-OCR 服务未启动
- OCR 服务地址配置错误

**解决方案：**
```bash
# 检查 OCR 服务状态
curl "http://127.0.0.1:1224/api/ocr/get_options"

# 修改 OCR 服务地址
# 编辑 services/ocr_service.py 中的 ocr_url
```

#### 3. 图片识别失败

**可能原因：**
- 图片格式不支持
- 文件大小超限（10MB）
- 图片内容无法识别

**解决方案：**
```bash
# 检查支持的格式
# 支持：jpg, jpeg, png, bmp, tiff, webp

# 压缩图片
# 使用工具将图片压缩到 10MB 以下
```

#### 4. 网络连接问题

**错误信息：**
```
连接被拒绝 (Connection refused)
```

**解决方案：**
- 确认服务已启动
- 检查防火墙设置
- 验证 IP 地址和端口

### 日志查看

服务启动后会显示详细日志，包括：
- 请求处理信息
- OCR 服务调用状态
- 错误详情和堆栈信息

示例日志：
```
2024-01-01 12:00:00 - uvicorn.error - INFO - Started server process [12345]
2024-01-01 12:00:01 - uvicorn.error - INFO - Waiting for application startup.
2024-01-01 12:00:02 - __main__ - INFO - OCR API服务启动
```

## � 开发指南

### 扩展 API 接口

在 `main.py` 中添加新的路由：

```python
@app.post("/custom/endpoint")
async def custom_endpoint():
    # 自定义逻辑
    return {"message": "自定义接口"}
```

### 修改数据模型

编辑 `models/ocr_models.py`：

```python
from pydantic import BaseModel

class CustomRequest(BaseModel):
    field1: str
    field2: int = 0
```

### 添加图片处理功能

在 `utils/image_utils.py` 中实现：

```python
def custom_image_process(image_data: bytes) -> bytes:
    # 自定义图片处理逻辑
    return processed_data
```

### 部署建议

#### 开发环境
```bash
python main.py
```

#### 生产环境
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📚 相关文档

- [客户端使用说明](ocr_client使用说明.md) - Umi-OCR Python 客户端详细使用指南
- [PaddleOCR集成说明](PaddleOCR集成说明.md) - PaddleOCR 集成详细说明和使用指南
- [Umi-OCR API 文档](Umi-api文档.md) - 原始 OCR API 参考
- [Swagger API 文档](http://localhost:8000/docs) - 交互式 API 文档

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 技术支持

如遇到问题，请按以下顺序检查：

1. 📖 查阅本文档和相关说明文档
2. 🔍 检查服务启动日志和错误信息
3. 🧪 使用测试页面验证服务状态
4. 🌐 确认 Umi-OCR 服务正常运行
5. 💬 提交 Issue 并提供详细的错误信息

---

**注意：** 使用前请确保 Umi-OCR 服务正在运行并可访问。默认地址：http://127.0.0.1:1224
