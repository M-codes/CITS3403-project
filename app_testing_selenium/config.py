import os

class Config:
    SECRET_KEY= '960610Moon'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 18 * 1024 * 1024  # 16 MB
    RECAPTCHA_ENABLED = True
class TestConfig(Config):
    TESTING = True 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    RECAPTCHA_ENABLED = False
    WTF_CSRF_ENABLED = False 
