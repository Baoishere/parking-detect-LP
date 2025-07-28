import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en')

def read_plate(im):
    result = ocr.ocr(im)
    if not result or not result[0][1]:
        return "unknown"
    # Lấy tất cả các dòng có độ tin cậy cao, sắp xếp theo vị trí y (từ trên xuống dưới)
    lines = []
    for line in result[0]:
        text, conf = line[1][0], line[1][1]
        if conf > 0.5:
            y_center = (line[0][0][1] + line[0][2][1]) / 2  # Trung bình y của box
            lines.append((y_center, text))
    if not lines:
        return "unknown"
    # Sắp xếp theo y tăng dần (từ trên xuống dưới)
    lines = sorted(lines, key=lambda x: x[0])
    # Ghép các dòng lại, phân tách bằng dấu cách hoặc xuống dòng
    return ' '.join([l[1] for l in lines])