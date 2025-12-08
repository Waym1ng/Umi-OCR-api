import json
import requests
import logging
from typing import Dict, Any, Optional
from models.ocr_models import OCRRequest, OCRResponse, OCROptions, OCRTextBlock

logger = logging.getLogger(__name__)


class OCRService:
    """OCR服务调用类"""
    
    def __init__(self, ocr_url: str = "http://127.0.0.1:1224/api/ocr"):
        self.ocr_url = ocr_url
        self.timeout = 60  # 请求超时时间（秒）
    
    async def recognize_image(self, request: OCRRequest) -> OCRResponse:
        """
        调用OCR服务进行图片识别
        
        Args:
            request: OCR请求对象
            
        Returns:
            OCRResponse: OCR识别结果
            
        Raises:
            Exception: OCR服务调用失败时
        """
        try:
            # 构建请求数据
            payload = {
                "base64": request.base64
            }
            
            # 添加选项参数
            if request.options:
                options_dict = self._convert_options_to_dict(request.options)
                if options_dict:
                    payload["options"] = options_dict
            
            logger.info(f"调用OCR服务: {self.ocr_url}")
            logger.debug(f"请求数据: base64长度={len(request.base64)}, options={payload.get('options', {})}")
            
            # 发送请求
            response = requests.post(
                self.ocr_url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            # 检查HTTP状态
            response.raise_for_status()
            
            # 解析响应
            result_dict = response.json()
            logger.info(f"OCR服务响应成功，状态码: {result_dict.get('code')}")
            
            # 转换为OCRResponse对象
            return self._convert_response(result_dict)
            
        except requests.exceptions.Timeout:
            logger.error("OCR服务请求超时")
            raise Exception("OCR服务请求超时")
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到OCR服务")
            raise Exception("无法连接到OCR服务，请确保OCR服务正在运行")
        except requests.exceptions.HTTPError as e:
            logger.error(f"OCR服务HTTP错误: {e}")
            raise Exception(f"OCR服务HTTP错误: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"OCR服务响应解析失败: {e}")
            raise Exception(f"OCR服务响应格式错误: {e}")
        except Exception as e:
            logger.error(f"OCR服务调用失败: {e}")
            raise Exception(f"OCR识别失败: {e}")
    
    def _convert_options_to_dict(self, options: OCROptions) -> Dict[str, Any]:
        """
        将OCROptions对象转换为字典格式
        
        Args:
            options: OCR选项对象
            
        Returns:
            Dict[str, Any]: 选项字典
        """
        options_dict = {}
        
        # 处理各个选项字段
        if options.ocr_language is not None:
            options_dict["ocr.language"] = options.ocr_language
        if options.ocr_cls is not None:
            options_dict["ocr.cls"] = options.ocr_cls
        # if options.ocr_limit_side_len is not None:
            # options_dict["ocr.limit_side_len"] = options.ocr_limit_side_len
        if options.tbpu_parser is not None:
            options_dict["tbpu.parser"] = options.tbpu_parser
        if options.tbpu_ignoreArea is not None:
            options_dict["tbpu.ignoreArea"] = options.tbpu_ignoreArea
        if options.data_format is not None:
            options_dict["data.format"] = options.data_format.value
        
        # 强制设置极大值以避免服务端限制
        options_dict["ocr.limit_side_len"] = 999999
            
        return options_dict
    
    def _convert_response(self, result_dict: Dict[str, Any]) -> OCRResponse:
        """
        将OCR服务响应字典转换为OCRResponse对象
        
        Args:
            result_dict: OCR服务响应字典
            
        Returns:
            OCRResponse: 标准化的OCR响应对象
        """
        # 处理data字段
        data = result_dict.get("data")
        
        # 如果是字符串（错误信息或纯文本），直接使用
        if isinstance(data, str):
            processed_data = data
        # 如果是列表，转换为OCRTextBlock对象列表
        elif isinstance(data, list):
            processed_data = []
            for item in data:
                if isinstance(item, dict):
                    text_block = OCRTextBlock(
                        text=item.get("text", ""),
                        score=item.get("score", 0.0),
                        box=item.get("box", []),
                        end=item.get("end", "")
                    )
                    processed_data.append(text_block)
                else:
                    logger.warning(f"跳过无效的文本块: {item}")
        else:
            processed_data = str(data) if data is not None else ""
        
        return OCRResponse(
            code=result_dict.get("code", 0),
            data=processed_data,
            time=result_dict.get("time", 0.0),
            timestamp=result_dict.get("timestamp", 0.0)
        )
    
    async def get_ocr_options(self) -> Dict[str, Any]:
        """
        获取OCR服务的参数选项
        
        Returns:
            Dict[str, Any]: 参数选项字典
        """
        try:
            url = self.ocr_url.replace("/api/ocr", "/api/ocr/get_options")
            logger.info(f"获取OCR参数选项: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            options_dict = response.json()
            logger.info("成功获取OCR参数选项")
            return options_dict
            
        except Exception as e:
            logger.error(f"获取OCR参数选项失败: {e}")
            raise Exception(f"获取OCR参数选项失败: {e}")


# 创建全局OCR服务实例
ocr_service = OCRService()
