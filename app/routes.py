from app import app
from flask import render_template, request, redirect, url_for, send_from_directory

import os
import pandas as pd
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename

@app.route('/')
@app.route('/index')

def index():
    return render_template("login.html")

@app.route('/upload_page')
def upload_page():
    # Ensure the upload folder exists
    return render_template("upload.html")

@app.route('/forum')
def forum():
    return render_template("forum.html")



@app.route('/plot')
def plot():
    # Serve the plot image from the 'static' folder
    return send_from_directory('static', 'plot.png')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        df = pd.read_csv(filepath)
        print(df.head())  # 🔍 Check structure
        print(df.dtypes)  # 🔍 Check data types

        # Try converting all columns except the first (index) to numeric
        df.set_index(df.columns[0], inplace=True)
        df = df.apply(pd.to_numeric, errors='coerce')  # Force numeric, set non-numeric to NaN

        if df.dropna(axis=1, how='all').empty:
            return "No numeric data to plot in uploaded file.", 400

        df.T.plot(figsize=(12, 6))
        plt.xlabel("Date")
        plt.ylabel("Excess Deaths per 100,000")
        plt.title("COVID-19 Excess Deaths")
        plt.tight_layout()

        # Ensure static/ folder exists
        static_folder = os.path.join(app.root_path, 'static')
        os.makedirs(static_folder, exist_ok=True)

        plot_path = os.path.join(static_folder, 'plot.png')
        plt.savefig(plot_path)
        plt.close()

        return render_template('result.html', plot_url='plot.png')
    return "Invalid file format", 400
