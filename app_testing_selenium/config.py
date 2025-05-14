import os

class Config:
    SECRET_KEY= '960610Moon'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 18 * 1024 * 1024  # 16 MB
    TESTING = False

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False  # if you're using Flask-WTF CSRF
