from flask import Flask
import mysql.connector
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = '2200001314'

# Kết nối trực tiếp với mysql.connector thay vì Flask-MySQLdb
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="baoishere",  # hoặc password="" nếu XAMPP không có password
    database="parkingdb"
)

try:
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        ('admin', generate_password_hash('123456'))
    )
    db.commit()
    print("Admin user created successfully!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    cursor.close()
    db.close()