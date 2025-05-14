from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config, TestConfig
import os
from flask_wtf.csrf import CSRFProtect
import warnings

warnings.filterwarnings("ignore", message=".*longdouble.*")

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()

def create_app(testing=False):
    app = Flask(__name__)
    app.secret_key = '960610Moon'

    # Load testing or default config
    if testing:
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(Config)

    csrf.init_app(app)
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
