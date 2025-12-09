import logging
import logging.handlers
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from models.ocr_models import (
    OCRRequest, 
    OCRResponse, 
    OCROptions, 
    ImageUploadResponse,
    ErrorResponse
)
from services.ocr_service import ocr_service
from utils.image_utils import image_to_base64, validate_image_file, clean_base64_string


def configure_application_logging():
    """配置应用程序日志，防止被其他库覆盖"""
    # 清除现有的根日志处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 配置根日志记录器
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # 配置第三方库的日志级别
    third_party_loggers = [
        'uvicorn',
        'uvicorn.access',
        'uvicorn.error',
        'fastapi',
        'paddleocr',
        'paddle',
        'ppocr',
        'requests',
        'urllib3'
    ]
    
    for logger_name in third_party_loggers:
        try:
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.setLevel(logging.WARNING)
        except:
            pass
    
    # 配置应用程序专用日志记录器
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.INFO)
    
    return app_logger


# 配置应用程序日志
logger = configure_application_logging()
logger.info("应用程序日志配置完成")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("OCR API服务启动")
    yield
    # 关闭时执行
    logger.info("OCR API服务关闭")


# 创建FastAPI应用
app = FastAPI(
    title="OCR文字识别API",
    description="基于Umi-OCR的文字识别服务API",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 允许所有源
    allow_credentials=True,      # 允许携带凭据
    allow_methods=["*"],         # 允许所有HTTP方法
    allow_headers=["*"],         # 允许所有请求头
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "OCR文字识别API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "recognize_upload": "/ocr/recognize",
            "recognize_base64": "/ocr/recognize/base64",
            "get_options": "/ocr/options",
            "test_page": "/test"
        }
    }


@app.get("/test")
async def redirect_to_test_page():
    """重定向到OCR测试页面"""
    return RedirectResponse(url="/static/test.html")


@app.post("/ocr/recognize", response_model=ImageUploadResponse)
async def recognize_uploaded_image(
    file: UploadFile = File(..., description="要识别的图片文件"),
    ocr_engine: str = Form("umi_ocr", alias="ocr.engine"),
    ocr_language: str = Form(None, alias="ocr.language"),
    ocr_cls: bool = Form(None, alias="ocr.cls"),
    ocr_limit_side_len: int = Form(None, alias="ocr.limit_side_len"),
    tbpu_parser: str = Form(None, alias="tbpu.parser"),
    data_format: str = Form("dict", alias="data.format"),
    paddleocr_device: str = Form("gpu", alias="paddleocr.device")
):
    """
    通过上传图片文件进行OCR识别
    
    - **file**: 要识别的图片文件（支持jpg, png, bmp, tiff, webp格式）
    - **ocr.language**: 语言/模型库（可选）
    - **ocr.cls**: 纠正文本方向（可选）
    - **ocr.limit_side_len**: 限制图像边长（可选）
    - **tbpu.parser**: 排版解析方案（可选）
    - **data.format**: 数据返回格式，dict或text（可选，默认dict）
    """
    try:
        # 验证图片文件
        if not validate_image_file(file):
            raise HTTPException(status_code=400, detail="无效的图片文件或文件过大（最大10MB）")
        
        # 重置文件指针到开始位置（validate_image_file可能会移动指针）
        file.file.seek(0)
        
        # 转换为base64
        base64_image = image_to_base64(file)
        
        # 构建OCR选项
        options = OCROptions(
            ocr_engine=ocr_engine,
            ocr_language=ocr_language,
            ocr_cls=ocr_cls,
            ocr_limit_side_len=ocr_limit_side_len,
            tbpu_parser=tbpu_parser,
            data_format=data_format,
            paddleocr_device=paddleocr_device
        )
        
        # 创建OCR请求
        ocr_request = OCRRequest(
            base64=base64_image,
            options=options if any([ocr_engine != "umi_ocr", ocr_language, ocr_cls, ocr_limit_side_len, tbpu_parser, data_format != "dict", paddleocr_device != "gpu"]) else None
        )
        
        # 调用OCR服务
        ocr_result = await ocr_service.recognize_image(ocr_request)
        
        logger.info(f"图片识别完成: {file.filename}, 状态码: {ocr_result.code}, 数据格式：{data_format}")
        # logger.info(f"图片识别结果: {ocr_result.data}")
        
        # 如果请求的是纯文本格式且识别成功，检查数据类型并处理
        if data_format == "text" and ocr_result.code == 100:
            from fastapi.responses import PlainTextResponse
            
            # 如果data是列表，手动拼接为纯文本
            if isinstance(ocr_result.data, list):
                text_parts = []
                for item in ocr_result.data:
                    if hasattr(item, 'text'):
                        text = item.text
                        end = getattr(item, 'end', '')
                        text_parts.append(text + end)
                plain_text = "".join(text_parts)
                logger.info(f"手动拼接OCR文本块，结果长度: {len(plain_text)}")
                return PlainTextResponse(
                    content=plain_text,
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
            else:
                # 如果已经是字符串，直接返回
                return PlainTextResponse(
                    content=str(ocr_result.data),
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
        
        return ImageUploadResponse(
            message="图片识别成功",
            ocr_result=ocr_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"图片识别失败: {str(e)}")


@app.post("/ocr/recognize/base64", response_model=OCRResponse)
async def recognize_base64_image(request: OCRRequest):
    """
    通过base64编码的图片进行OCR识别
    
    - **base64**: Base64编码的图片数据（无需前缀）
    - **options**: OCR识别选项（可选）
    """
    try:
        # 清理base64字符串
        cleaned_base64 = clean_base64_string(request.base64)
        if not cleaned_base64:
            raise HTTPException(status_code=400, detail="无效的base64图片数据")
        
        # 更新请求中的base64数据
        request.base64 = cleaned_base64
        
        # 调用OCR服务
        result = await ocr_service.recognize_image(request)
        
        logger.info(f"Base64图片识别完成，状态码: {result.code}")
        logger.info(f"Base64图片识别: {result}")
        
        # 如果请求的是纯文本格式且识别成功，检查数据类型并处理
        if request.options and request.options.data_format and request.options.data_format.value == "text" and result.code == 100:
            from fastapi.responses import PlainTextResponse
            
            # 如果data是列表，手动拼接为纯文本
            if isinstance(result.data, list):
                text_parts = []
                for item in result.data:
                    if hasattr(item, 'text'):
                        text = item.text
                        end = getattr(item, 'end', '')
                        text_parts.append(text + end)
                plain_text = "".join(text_parts)
                logger.info(f"base64接口手动拼接OCR文本块，结果长度: {len(plain_text)}")
                return PlainTextResponse(
                    content=plain_text,
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
            else:
                # 如果已经是字符串，直接返回
                return PlainTextResponse(
                    content=str(result.data),
                    headers={"Content-Type": "text/plain; charset=utf-8"}
                )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Base64图片识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"图片识别失败: {str(e)}")


@app.get("/ocr/options")
async def get_ocr_options():
    """
    获取OCR服务的参数选项信息
    
    返回所有可用的OCR参数定义、默认值、可选值等信息
    """
    try:
        options = await ocr_service.get_ocr_options()
        return {
            "message": "成功获取OCR参数选项",
            "options": options
        }
    except Exception as e:
        logger.error(f"获取OCR参数选项失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取OCR参数选项失败: {str(e)}")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 尝试连接OCR服务
        await ocr_service.get_ocr_options()
        return {
            "status": "healthy",
            "ocr_service": "connected"
        }
    except Exception as e:
        logger.warning(f"OCR服务连接检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "ocr_service": "disconnected",
                "error": str(e)
            }
        )


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
