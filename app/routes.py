from flask import Blueprint, render_template, request, current_app
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px
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
        upload_folder = current_app.config['UPLOAD_FOLDER']

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        if df.dropna(axis=1, how='all').empty:
            return "No numeric data to plot.", 400

        # Save to DB
        for index, row in df.iterrows():
            region = row["Entity"]
            date_str = row["Day"]
            value = row["Cumulative excess deaths per 100,000 people (central estimate)"]
            if pd.notnull(value):
                exists = DataPoint.query.filter_by(region=region, date=date_str).first()
                if not exists:
                    point = DataPoint(region=region, date=date_str, value=value)
                    db.session.add(point)
        db.session.commit()

        # --- Plot choropleth map using Plotly ---
        fig = px.choropleth(
            df,
            locations="Entity",
            locationmode="country names",
            color="Cumulative excess deaths per 100,000 people (central estimate)",
            hover_name="Entity",
            color_continuous_scale="Reds",
            title="Cumulative Excess Deaths per 100,000 People (Central Estimate)"
        )

        static_folder = os.path.join(current_app.root_path, 'static')
        os.makedirs(static_folder, exist_ok=True)
        map_path = os.path.join(static_folder, 'map_plot.html')
        fig.write_html(map_path)

        return render_template('result.html', plot_url='map_plot.html')

    return "Invalid file format", 400
