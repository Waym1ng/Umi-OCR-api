import base64
import io
from typing import Union
from fastapi import UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile
import logging

logger = logging.getLogger(__name__)


def image_to_base64(image_data: Union[bytes, UploadFile]) -> str:
    """
    将图片数据转换为base64编码字符串
    
    Args:
        image_data: 图片字节数据或UploadFile对象
        
    Returns:
        str: base64编码字符串（不含前缀）
        
    Raises:
        ValueError: 当图片数据无效时
    """
    try:
        logger.info(f"开始处理图片数据，类型: {type(image_data)}")
        
        # 检查是否为UploadFile对象（支持FastAPI和Starlette的UploadFile）
        if isinstance(image_data, (UploadFile, StarletteUploadFile)):
            # 如果是UploadFile对象，确保文件指针在开始位置
            logger.info(f"处理UploadFile对象: {image_data.filename}")
            image_data.file.seek(0)
            image_bytes = image_data.file.read()
            
            # 检查是否成功读取了数据
            if not image_bytes:
                raise ValueError("无法读取上传文件的内容，文件可能为空或已损坏")
                
            logger.info(f"成功读取UploadFile，大小: {len(image_bytes)} bytes")
        else:
            # 如果是字节数据
            image_bytes = image_data
            
            # 检查字节数据是否有效
            if not image_bytes:
                raise ValueError("图片字节数据为空")
                
            logger.info(f"接收到字节数据，大小: {len(image_bytes)} bytes")
            
        # 转换为base64
        base64_str = base64.b64encode(image_bytes).decode('utf-8')
        
        logger.info(f"成功将图片转换为base64，长度: {len(base64_str)}")
        return base64_str
        
    except Exception as e:
        logger.error(f"图片转base64失败: {str(e)}")
        import traceback
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        raise ValueError(f"图片处理失败: {str(e)}")


def validate_image_file(file: UploadFile) -> bool:
    """
    验证上传的文件是否为有效的图片格式
    
    Args:
        file: UploadFile对象
        
    Returns:
        bool: 是否为有效图片
    """
    # 支持的图片格式
    allowed_types = [
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/bmp',
        'image/tiff',
        'image/webp'
    ]
    
    # 检查文件类型
    if file.content_type not in allowed_types:
        logger.warning(f"不支持的文件类型: {file.content_type}")
        return False
    
    # 检查文件大小（限制为10MB）
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置文件指针
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        logger.warning(f"文件过大: {file_size} bytes，最大允许: {max_size} bytes")
        return False
    
    logger.info(f"图片验证通过: {file.filename}, 类型: {file.content_type}, 大小: {file_size} bytes")
    return True


def clean_base64_string(base64_str: str) -> str:
    """
    清理base64字符串，移除可能的前缀
    
    Args:
        base64_str: 可能包含前缀的base64字符串
        
    Returns:
        str: 清理后的base64字符串
    """
    # 移除data:image/xxx;base64,前缀
    if ',' in base64_str:
        base64_str = base64_str.split(',', 1)[1]
    
    # 移除空白字符
    base64_str = base64_str.strip()
    
    return base64_str
