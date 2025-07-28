from flask import Flask
import mysql.connector
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = '' # Đặt secret key cho Flask
password = '' # Đặt mật khẩu cho admin

# Kết nối trực tiếp với mysql.connector thay vì Flask-MySQLdb
db = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="",  # hoặc password="" nếu XAMPP không có password
    database="" # Đặt tên database của bạn ở đây, ví dụ: "parkingdb"
)

try:
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        ('admin', generate_password_hash(password, method='sha256'))
    )
    db.commit()
    print("Admin user created successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    db.close()
