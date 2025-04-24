from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config  # <--- import your config class
import os
import warnings

warnings.filterwarnings("ignore", message=".*longdouble.*")

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # <--- load config from the class

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app