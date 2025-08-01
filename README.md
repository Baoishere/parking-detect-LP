# Parking License Plate Recognition WebApp

## Mô tả

Đây là dự án web quản lý bãi giữ xe thông minh sử dụng Flask, YOLOv5 để phát hiện biển số xe và PaddleOCR để nhận diện ký tự trên biển số. Nhân viên có thể đăng nhập, ghi nhận xe vào/ra bằng ảnh, lưu trữ lịch sử vào cơ sở dữ liệu MySQL.

---

## Tính năng

- Đăng nhập nhân viên
- Nhận diện biển số xe tự động từ ảnh (YOLOv5 + PaddleOCR)
- Ghi nhận xe vào/ra, lưu ảnh và thông tin vào database
- Quản lý lịch sử xe vào/ra
- Giao diện web đơn giản, dễ sử dụng

---

## Cài đặt

### 1. Cài đặt Python và các thư viện

- Python >= 3.8
- Tạo môi trường ảo (khuyến nghị):

    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

- Cài đặt các thư viện:

    ```bash
    pip install -r requirements.txt
    ```

- Nếu dùng GPU cho PaddleOCR, cài thêm paddlepaddle-gpu theo hướng dẫn:  
  https://www.paddlepaddle.org.cn/install/quick

### 2. Chuẩn bị mô hình

- **Mô hình được đào tạo trước từ liên kết này:** [Models](https://drive.google.com/drive/folders/1qB8QYr-b-PWsXMO0K3mef66P_kXfhfmM?usp=sharing)

- **Tải xuống yolov5 (phiên bản cũ) từ liên kết này:** [yolov5](https://drive.google.com/drive/folders/16Urwqj_x9Y_3KWLcc1cKMDOdYdhaQhxx?usp=sharing)

- Sao chép yolov5 và thư mục model vào thư mục dự án

- **Hướng dẫn huấn luyện mô hình có tại repo:** [license-plate-recognition](https://github.com/Baoishere/license-plate-recognition)

### 3. Khởi tạo database

- Tạo database MySQL tên `parkingdb`.
- Import file `parkingdb.sql` để tạo bảng và tài khoản mẫu:

    ```bash
    mysql -u root -p parkingdb < parkingdb.sql
    ```

- Thông tin đăng nhập mặc định:  
  - Username: `admin`  
  - Password: (đã mã hóa, đổi trong database nếu cần)

### 4. Cấu hình

- Sửa file `config.py` với thông tin kết nối MySQL phù hợp:

    ```python
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'your_password'
    MYSQL_DB = 'parkingdb'
    SECRET_KEY = 'your_secret_key'
    ```

### 5. Chạy ứng dụng

```bash
python app.py
```

Truy cập [http://127.0.0.1:5000](http://127.0.0.1:5000) trên trình duyệt.

---

## Cấu trúc thư mục

```
Parking/
├── app.py
├── config.py
├── db_models.py
├── requirements.txt
├── parkingdb.sql
├── model/
│   └── LP_detector.pt
├── static/
│   └── style.css
├── templates/
│   ├── index.html
│   └── login.html
├── routes/
│   ├── auth.py
│   └── parking.py
├── function/
│   ├── helper.py
│   └── utils_rotate.py
└── yolov5/
    └── ... (YOLOv5 code)
```

---

## Ghi chú
- Đảm bảo đã cài đặt MySQL và tạo database `parkingdb` trước khi chạy ứng dụng.
- CSS, JS để trong `static/`.
- Nếu gặp lỗi về import YOLOv5, đảm bảo đã thêm đường dẫn `yolov5/` vào `sys.path` trong code.
- Đảm bảo PaddleOCR và các model đã cài đặt đúng phiên bản.
- Sửa file yolov5\models\experimental.py
   ```bash
    ckpt = torch.load(attempt_download(w), map_location=map_location)
    ```
   Thành
   ```bash
    ckpt = torch.load(attempt_download(w), map_location=map_location, weights_only=False)
    ```
---

## Đóng góp & Liên hệ

- Đóng góp code, báo lỗi hoặc ý tưởng mới vui lòng tạo issue hoặc pull request trên repository.
- Liên hệ: [baoishere@outlook.com]

---
