from flask import Flask
from config import Config
from routes.auth import auth_bp
from routes.parking import parking_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(parking_bp)

if __name__ == '__main__':
    app.run(debug=True)