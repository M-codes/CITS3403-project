from flask import Blueprint, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib.pyplot as plt
import os

from app import db
from app.models import DataPoint


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template("login.html")

@bp.route('/upload_page')
def upload_page():
    return render_template("upload.html")

@bp.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        upload_folder = request.app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        df = pd.read_csv(filepath)
        df.set_index(df.columns[0], inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')

        if df.dropna(axis=1, how='all').empty:
            return "No numeric data to plot.", 400

        df.T.plot(figsize=(12, 6))
        plt.title("Uploaded Data Plot")
        plt.tight_layout()
        plot_path = os.path.join('static', 'plot.png')
        plt.savefig(plot_path)
        plt.close()

        return render_template('result.html', plot_url='plot.png')
    return "Invalid file format", 400
