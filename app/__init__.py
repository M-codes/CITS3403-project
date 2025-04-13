from flask import Flask
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')  # or 'static/uploads' if you prefer

# Make sure the folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from app import routes
