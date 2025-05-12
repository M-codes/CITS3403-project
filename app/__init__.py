from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config  # <--- import your config class
import os
import warnings

warnings.filterwarnings("ignore", message=".*longdouble.*")

db = SQLAlchemy()
migrate = Migrate()
def create_app():
    app = Flask(__name__)
    app.secret_key = '960610Moon'
    
    # Configs
    app.config.from_object(Config)  # <--- load config from the class
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['RECAPTCHA_SECRET_KEY'] = '6LfnCi8rAAAAAMHL8op0mE8gL-gXKyXjoLTuckbX'

    
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})
    

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from app import routes
    app.register_blueprint(routes.bp)


    return app