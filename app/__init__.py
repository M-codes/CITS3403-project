from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import Config  # <--- import your config class
import os
import warnings

warnings.filterwarnings("ignore", message=".*longdouble.*")

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = '960610Moon'
    
    # Configs
    app.config.from_object(Config)  # <--- load config from the class
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})
    

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)

    db.init_app(app)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app