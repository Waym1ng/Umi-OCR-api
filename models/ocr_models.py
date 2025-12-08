from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class OCRDataFormat(str, Enum):
    DICT = "dict"
    TEXT = "text"


class OCROptions(BaseModel):
    """OCR识别选项"""
    ocr_language: Optional[str] = Field(None, alias="ocr.language")
    ocr_cls: Optional[bool] = Field(None, alias="ocr.cls")
    ocr_limit_side_len: Optional[int] = Field(None, alias="ocr.limit_side_len")
    tbpu_parser: Optional[str] = Field(None, alias="tbpu.parser")
    tbpu_ignoreArea: Optional[List[List[List[int]]]] = Field(None, alias="tbpu.ignoreArea")
    data_format: Optional[OCRDataFormat] = Field(OCRDataFormat.DICT, alias="data.format")


class OCRRequest(BaseModel):
    """OCR请求模型"""
    base64: str = Field(..., description="Base64编码的图片数据")
    options: Optional[OCROptions] = Field(None, description="OCR识别选项")


class OCRTextBlock(BaseModel):
    """OCR文本块模型"""
    text: str = Field(..., description="识别的文本")
    score: float = Field(..., description="置信度")
    box: List[List[int]] = Field(..., description="文本框坐标")
    end: str = Field(..., description="结束符")


class OCRResponse(BaseModel):
    """OCR响应模型"""
    code: int = Field(..., description="状态码")
    data: Union[str, List[OCRTextBlock]] = Field(..., description="识别结果")
    time: float = Field(..., description="识别耗时（秒）")
    timestamp: float = Field(..., description="任务开始时间戳（秒）")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误信息")
    detail: Optional[str] = Field(None, description="详细错误信息")


class ImageUploadResponse(BaseModel):
    """图片上传响应模型"""
    message: str = Field(..., description="响应消息")
    ocr_result: Optional[OCRResponse] = Field(None, description="OCR识别结果")
