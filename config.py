class Config:
    SECRET_KEY = '' # Đặt secret key cho Flask (giống như app.secret_key)
    MYSQL_HOST = 'localhost' 
    MYSQL_USER = 'root' 
    MYSQL_PASSWORD = ''  # Hoặc password="" nếu XAMPP không có password
    MYSQL_DB = '' # Đặt tên database của bạn ở đây, ví dụ: "parkingdb"
