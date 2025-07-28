import cv2
import numpy as np
from function.helper import read_plate
from function.utils_rotate import deskew
import torch
from paddleocr import PaddleOCR

# Khởi tạo model toàn cục (hoặc truyền vào hàm nếu muốn)
yolo_LP_detect = torch.hub.load(
    'yolov5', 'custom', path='models/LP_detector.pt', force_reload=True, source='local'
)
ocr = PaddleOCR(use_angle_cls=True, lang='en')

def detect_plates_and_draw(img):
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    detected_plates = []
    img_result = img.copy()
    if not list_plates:
        return detected_plates, img_result
    for plate in list_plates:
        x, y, w, h = int(plate[0]), int(plate[1]), int(plate[2] - plate[0]), int(plate[3] - plate[1])
        crop_img = img[y:y + h, x:x + w]
        if (crop_img is None or crop_img.size == 0 or
            len(crop_img.shape) != 3 or crop_img.shape[2] != 3 or
            crop_img.shape[0] < 10 or crop_img.shape[1] < 10 or
            crop_img.dtype != np.uint8):
            continue
        try:
            lp_text = read_plate(crop_img)
        except Exception as e:
            print("OCR error:", e)
            continue
        if lp_text != "unknown":
            detected_plates.append(lp_text)
            cv2.putText(img_result, lp_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            cv2.rectangle(img_result, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return detected_plates, img_result