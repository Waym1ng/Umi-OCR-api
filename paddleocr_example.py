from paddleocr import PaddleOCR
import sys
import os


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    device="gpu"
)

def extract_text(img_path):
    result = ocr.predict(input=img_path)
    texts = []
    for res in result:
        # res 可能是对象，也可能是 dict depending on version
        text = getattr(res, "rec_text", None) or (res.get("rec_text") if isinstance(res, dict) else None)
        if text is None:
            # 回退到旧结构
            recs = res.get("rec_texts") if isinstance(res, dict) else None
            if recs:
                texts.extend(recs)
            continue
        texts.append(text)
    merged_text = " ".join(texts)
    return merged_text

# 传入图片路径（作为命令行参数）
image_path = sys.argv[1]
merged_text = extract_text(image_path)
print("Merged text:", merged_text)
# 示例用法：
# python paddleocr_client.py "D:\Code\OCR\t.png"