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

@bp.route('/data_table')
def data_table():
    data = DataPoint.query.order_by(DataPoint.date.desc()).all()
    return render_template('data_table.html', data=data)


@bp.route('/upload_page')
def upload_page():
    return render_template("upload.html")

@bp.route('/manual_entry', methods=['GET', 'POST'])
def manual_entry():
    if request.method == 'POST':
        region = request.form.get('region')
        date_str = request.form.get('date')
        value = request.form.get('value')

        try:
            value = float(value)
        except (ValueError, TypeError):
            return "Invalid value for excess deaths.", 400

        if region and date_str and pd.notnull(value):
            exists = DataPoint.query.filter_by(region=region, date=date_str).first()
            if not exists:
                point = DataPoint(region=region, date=date_str, value=value)
                db.session.add(point)
                db.session.commit()
                return render_template('entry_success.html', region=region, date=date_str, value=value)
            else:
                return "Data point already exists.", 400
        return "Missing or invalid input.", 400

    # GET request — grab distinct country names from the database
    country_list = [row[0] for row in db.session.query(DataPoint.region).distinct().order_by(DataPoint.region).all()]
    return render_template('manual_entry.html', countries=country_list)
    

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

@bp.route('/map')
def map_view():
    selected_date = request.args.get('date')

    if selected_date:
        df = pd.read_sql(db.session.query(DataPoint).filter_by(date=selected_date).statement, db.session.bind)
    else:
        df = pd.read_sql(db.session.query(DataPoint).statement, db.session.bind)

    if df.empty:
        return "No data for that date.", 404

    fig = px.choropleth(
        df,
        locations="region",
        locationmode="country names",
        color="value",
        hover_name="region",
        color_continuous_scale="Reds",
        title=f"Excess Deaths on {selected_date}" if selected_date else "All Data"
    )

    map_path = os.path.join(current_app.static_folder, 'map_plot.html')
    fig.write_html(map_path)
    return render_template('result.html', plot_url='map_plot.html')

