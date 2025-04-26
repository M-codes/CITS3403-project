from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import warnings
warnings.filterwarnings("ignore", message=".*longdouble.*")

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = '960610Moon'
    
    # Configs
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})
    

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize plugins
    db.init_app(app)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Import and register routes
    from app import routes
    app.register_blueprint(routes.bp)

    # Create DB tables
    with app.app_context():
        db.create_all()

    return app