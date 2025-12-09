import logging
import base64
import io
from typing import Dict, Any, Optional
from PIL import Image
import numpy as np
from models.ocr_models import OCRResponse, OCRTextBlock

logger = logging.getLogger(__name__)


def _configure_paddleocr_logging():
    """配置PaddleOCR的日志，防止覆盖应用日志"""
    # 设置PaddleOCR相关的日志级别为WARNING，减少输出噪音
    paddleocr_loggers = [
        'paddleocr',
        'paddle',
        'ppocr',
        'paddle.utils',
        'paddleocr.tools'
    ]
    
    for logger_name in paddleocr_loggers:
        try:
            paddle_logger = logging.getLogger(logger_name)
            paddle_logger.setLevel(logging.WARNING)
            # 防止日志传播到根记录器
            paddle_logger.propagate = False
        except:
            pass
    
    # 确保根记录器的格式正确
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        # 如果没有处理器，添加一个控制台处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)


class PaddleOCRService:
    """PaddleOCR服务类"""
    
    def __init__(self, device: str = "gpu"):
        """
        初始化PaddleOCR服务
        
        Args:
            device: 设备类型，"gpu"或"cpu"
        """
        self.device = device
        self.ocr = None
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """初始化PaddleOCR实例"""
        try:
            # 在初始化PaddleOCR前配置日志
            _configure_paddleocr_logging()
            
            from paddleocr import PaddleOCR
            
            # 临时设置环境变量来控制PaddleOCR的日志
            import os
            os.environ['FLAGS_logtostderr'] = '0'  # 禁用PaddlePaddle的日志输出
            os.environ['FLAGS_verbosity'] = '0'     # 设置详细级别为0
            
            self.ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                device=self.device,
                det_limit_side_len=1024*8,
            )
            logger.info(f"PaddleOCR初始化成功，使用设备: {self.device}")
            
            # 初始化后重新配置应用日志，确保格式正确
            _configure_paddleocr_logging()
            
        except ImportError:
            logger.error("PaddleOCR未安装，请运行: pip install paddleocr")
            raise Exception("PaddleOCR未安装")
        except Exception as e:
            logger.error(f"PaddleOCR初始化失败: {e}")
            raise Exception(f"PaddleOCR初始化失败: {e}")
    
    async def recognize_image(self, base64_image: str) -> OCRResponse:
        """
        使用PaddleOCR识别图片
        
        Args:
            base64_image: Base64编码的图片数据
            
        Returns:
            OCRResponse: OCR识别结果
        """
        import time
        start_time = time.time()
        
        try:
            # 解码base64图片
            image = self._decode_base64_image(base64_image)
            
            # 执行OCR识别
            result = self.ocr.predict(input=image)
            
            # 处理识别结果
            text_blocks = self._process_result(result)
            merged_text = " ".join([block.text for block in text_blocks])
            
            # 计算耗时
            processing_time = time.time() - start_time
            
            logger.info(f"PaddleOCR识别完成，耗时: {processing_time:.2f}秒，文本块数量: {len(text_blocks)}")
            
            # 返回统一格式的响应
            return OCRResponse(
                code=100,  # 成功状态码
                data=text_blocks,
                time=processing_time,
                timestamp=start_time
            )
            
        except Exception as e:
            logger.error(f"PaddleOCR识别失败: {e}")
            return OCRResponse(
                code=200,  # 错误状态码
                data=f"PaddleOCR识别失败: {str(e)}",
                time=time.time() - start_time,
                timestamp=start_time
            )
    
    def _decode_base64_image(self, base64_string: str) -> np.ndarray:
        """
        解码base64图片为numpy数组
        
        Args:
            base64_string: Base64编码的图片数据
            
        Returns:
            np.ndarray: 图片数组
        """
        try:
            # 清理base64字符串（移除可能的前缀）
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # 解码base64
            image_data = base64.b64decode(base64_string)
            
            # 转换为PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB格式（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为numpy数组
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Base64图片解码失败: {e}")
            raise Exception(f"Base64图片解码失败: {e}")
    
    def _process_result(self, result) -> list:
        """
        处理PaddleOCR的识别结果
        
        Args:
            result: PaddleOCR返回的原始结果
            
        Returns:
            list: OCRTextBlock对象列表
        """
        text_blocks = []
        
        try:
            for res in result:
                # 尝试获取文本内容
                text = getattr(res, "rec_text", None)
                
                if text is None and isinstance(res, dict):
                    text = res.get("rec_text")
                
                if text is None:
                    # 回退到旧结构
                    if isinstance(res, dict):
                        recs = res.get("rec_texts")
                        if recs and isinstance(recs, list):
                            for rec_text in recs:
                                if rec_text:  # 只添加非空文本
                                    text_blocks.append(OCRTextBlock(
                                        text=rec_text,
                                        score=1.0,  # 默认置信度
                                        box=[],    # PaddleOCR示例中没有坐标信息
                                        end=" "    # 使用空格作为分隔符
                                    ))
                    continue
                
                # 获取置信度
                score = getattr(res, "rec_score", None)
                if score is None and isinstance(res, dict):
                    score = res.get("rec_score", 1.0)
                if score is None:
                    score = 1.0
                
                # 获取坐标信息（如果存在）
                box = getattr(res, "bbox", None)
                if box is None and isinstance(res, dict):
                    box = res.get("bbox", [])
                if box is None:
                    box = []
                
                # 创建文本块
                text_blocks.append(OCRTextBlock(
                    text=text,
                    score=float(score),
                    box=box,
                    end=" "  # 使用空格作为分隔符
                ))
                
        except Exception as e:
            logger.error(f"处理PaddleOCR结果失败: {e}")
            # 如果处理失败，返回错误信息作为文本块
            text_blocks.append(OCRTextBlock(
                text=f"结果处理失败: {str(e)}",
                score=0.0,
                box=[],
                end=""
            ))
        
        return text_blocks
    
    async def get_ocr_options(self) -> Dict[str, Any]:
        """
        获取PaddleOCR的参数选项
        
        Returns:
            Dict[str, Any]: 参数选项字典
        """
        return {
            "engine": "paddleocr",
            "device": self.device,
            "supported_formats": ["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
            "features": {
                "text_detection": True,
                "text_recognition": True,
                "multi_language": True,
                "gpu_acceleration": self.device == "gpu"
            },
            "parameters": {
                "device": {
                    "type": "string",
                    "options": ["cpu", "gpu"],
                    "default": self.device,
                    "description": "计算设备类型"
                }
            }
        }


# 创建全局PaddleOCR服务实例
paddleocr_service = PaddleOCRService()
