from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import cv2
import torch
from function.helper import read_plate
from function.utils_rotate import deskew
import numpy as np
from functools import wraps
from datetime import datetime
from db_models import get_db

yolo_LP_detect = torch.hub.load(
    'yolov5', 'custom', path='model/LP_detector.pt', force_reload=True, source='local'
)

parking_bp = Blueprint('parking', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@parking_bp.route('/')
@login_required
def home():
    return render_template('index.html', username=session.get('username'))

@parking_bp.route('/car_in', methods=['POST'])
@login_required
def car_in():
    file = request.files['file']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    detected_plates = []
    img_result = img.copy()
    if not list_plates:
        flash("Không nhận diện được biển số!", "danger")
        return render_template('index.html', username=session.get('username'))
    else:
        for plate in list_plates:
            x, y, w, h = int(plate[0]), int(plate[1]), int(plate[2] - plate[0]), int(plate[3] - plate[1])
            crop_img = img[y:y + h, x:x + w]
            # Kiểm tra crop_img hợp lệ
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
    time_in = datetime.now()
    image_in_path = f"in_{int(time_in.timestamp())}.jpg"
    cv2.imwrite(f"static/{image_in_path}", img_result)
    if detected_plates:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO parking_log (plate, image_in, time_in, user_in) VALUES (%s, %s, %s, %s)",
            (detected_plates[0], image_in_path, time_in, session['user_id'])
        )
        db.commit()
        cursor.close()
        db.close()
        flash("Xe vào đã được ghi nhận!", "success")
        return render_template('index.html', image_in=image_in_path, plate_in=detected_plates[0], username=session.get('username'))
    else:
        flash("Không nhận diện được biển số!", "danger")
        return render_template('index.html', username=session.get('username'))

@parking_bp.route('/car_out', methods=['POST'])
@login_required
def car_out():
    file = request.files['file']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    detected_plates = []
    img_result = img.copy()
    if not list_plates:
        flash("Không nhận diện được biển số!", "danger")
        return render_template('index.html', username=session.get('username'))
    else:
        for plate in list_plates:
            x, y, w, h = int(plate[0]), int(plate[1]), int(plate[2] - plate[0]), int(plate[3] - plate[1])
            crop_img = img[y:y + h, x:x + w]
            # Kiểm tra crop_img hợp lệ
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
    time_out = datetime.now()
    image_out_path = f"out_{int(time_out.timestamp())}.jpg"
    cv2.imwrite(f"static/{image_out_path}", img_result)
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM parking_log WHERE image_out IS NULL ORDER BY time_in DESC LIMIT 1"
    )
    log = cursor.fetchone()
    if log and detected_plates:
        plate_in = log['plate'].replace(" ", "").upper()
        plate_out_norm = detected_plates[0].replace(" ", "").upper()
        matched = int(plate_in == plate_out_norm)
        if matched:
            cursor.execute(
                "UPDATE parking_log SET image_out=%s, time_out=%s, user_out=%s, matched=%s WHERE id=%s",
                (image_out_path, time_out, session['user_id'], matched, log['id'])
            )
            db.commit()
        cursor.close()
        db.close()
        return render_template(
            'index.html',
            image_in=log['image_in'],
            plate_in=log['plate'],
            image_out=image_out_path,
            plate_out=detected_plates[0],
            matched=matched,
            username=session.get('username')
        )
    else:
        cursor.close()
        db.close()
        flash("Không tìm thấy xe vào phù hợp hoặc không nhận diện được biển số!", "danger")
        return render_template('index.html', username=session.get('username'))
    

@parking_bp.route('/confirm_match/<int:log_id>', methods=['POST'])
@login_required
def confirm_match(log_id):
    matched = bool(int(request.form['matched']))
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE parking_log SET matched=%s WHERE id=%s",
        (matched, log_id)
    )
    db.commit()
    cursor.close()
    db.close()
    flash("Đã xác nhận so khớp!", "success")
    return redirect(url_for('home'))

def detect_plate(img):
    # Nhận diện biển số bằng YOLOv5
    plates = yolo_LP_detect(img, size=640)
    list_plates = plates.pandas().xyxy[0].values.tolist()
    if not list_plates:
        return "unknown"
    for plate in list_plates:
        x1, y1, x2, y2 = int(plate[0]), int(plate[1]), int(plate[2]), int(plate[3])
        h, w = img.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        crop_img = img[y1:y2, x1:x2]
        # Kiểm tra crop_img hợp lệ
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
            return lp_text
    return "unknown"