from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
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
        lower = request.form.get('lower_bound')
        upper = request.form.get('upper_bound')
        confirmed = request.form.get('confirmed_deaths')

        try:
            value = float(value)
            lower = float(lower) if lower else None
            upper = float(upper) if upper else None
            confirmed = float(confirmed) if confirmed else None
        except ValueError:
            flash("Invalid numeric input.", 'error')
            return redirect(url_for('main.manual_entry'))

        if region and date_str and pd.notnull(value):
            exists = DataPoint.query.filter_by(region=region, date=date_str).first()
            if not exists:
                point = DataPoint(
                    region=region,
                    date=date_str,
                    value=value,
                    lower_bound=lower,
                    upper_bound=upper,
                    confirmed_deaths=confirmed
                )
                db.session.add(point)
                db.session.commit()
                return render_template(
                    'entry_success.html',
                    region=region,
                    date=date_str,
                    value=value,
                    lower=lower,
                    upper=upper,
                    confirmed=confirmed
                )
            else:
                flash("Data point already exists.", 'warning')
                return redirect(url_for('main.manual_entry'))
        flash("Missing or invalid input.", 'error')
        return redirect(url_for('main.manual_entry'))

    # GET: show form
    country_list = [row[0] for row in db.session.query(DataPoint.region).distinct().order_by(DataPoint.region).all()]
    return render_template('manual_entry.html', countries=country_list)

    

@bp.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            flash("Failed to read CSV file.", 'error')
            return redirect(url_for('main.upload_page'))

        if df.dropna(axis=1, how='all').empty:
            flash("No numeric data to plot.", 'warning')
            return redirect(url_for('main.upload_page'))

        for _, row in df.iterrows():
            region = row.get("Entity")
            date_str = row.get("Day")
            value = row.get("Cumulative excess deaths per 100,000 people (central estimate)")
            lower = row.get("Cumulative excess deaths per 100,000 people (95% CI, lower bound)")
            upper = row.get("Cumulative excess deaths per 100,000 people (95% CI, upper bound)")
            confirmed = row.get("Total confirmed deaths due to COVID-19 per 100,000 people")

            if pd.notnull(value):
                exists = DataPoint.query.filter_by(region=region, date=date_str).first()
                if not exists:
                    dp = DataPoint(
                        region=region,
                        date=date_str,
                        value=value,
                        lower_bound=lower,
                        upper_bound=upper,
                        confirmed_deaths=confirmed
                    )
                    db.session.add(dp)
        db.session.commit()

        fig = px.choropleth(
            df,
            locations="Entity",
            locationmode="country names",
            color="Cumulative excess deaths per 100,000 people (central estimate)",
            hover_name="Entity",
            hover_data={
                "Cumulative excess deaths per 100,000 people (95% CI, lower bound)": True,
                "Cumulative excess deaths per 100,000 people (95% CI, upper bound)": True,
                "Total confirmed deaths due to COVID-19 per 100,000 people": True
            },
            color_continuous_scale="Reds",
            title="Cumulative Excess Deaths per 100,000 People (Central Estimate)"
        )

        map_path = os.path.join(current_app.static_folder, 'map_plot.html')
        fig.write_html(map_path)
        return render_template('result.html', plot_url='map_plot.html')

    flash("Invalid file format. Please upload a CSV file.", 'error')
    return redirect(url_for('main.upload_page'))

@bp.route('/time_series')
def time_series():
    # Load all data using SQLAlchemy query
    data = db.session.query(DataPoint).all()

    if not data:
        return "No data available.", 404

    # Convert the data to a DataFrame
    df = pd.DataFrame([{
        'region': dp.region,
        'date': dp.date,
        'value': dp.value
    } for dp in data])

    # Optional: convert the 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])

    # Create a line plot for time series (Excess Deaths over Time)
    fig = px.line(
        df,
        x='date',
        y='value',
        title="Excess Deaths Over Time",
        labels={'date': 'Date', 'value': 'Excess Deaths per 100,000 People'},
        line_shape='linear'
    )

    # Save the plot as an HTML file
    plot_path = os.path.join(current_app.static_folder, 'time_series_plot.html')
    fig.write_html(plot_path)

    return render_template('result.html', plot_url='time_series_plot.html')





@bp.route('/map')
def map_view():
    selected_date = request.args.get('date')

    # Load all data using SQLAlchemy query
    data = db.session.query(DataPoint).all()

    if not data:
        return "No data available.", 404

    # Convert the data to a DataFrame
    df = pd.DataFrame([{
        'region': dp.region,
        'date': dp.date,
        'value': dp.value
    } for dp in data])

    # Optional: convert the 'date' column to string for Plotly compatibility
    df['date'] = df['date'].astype(str)

    fig = px.choropleth(
        df,
        locations="region",
        locationmode="country names",
        color="value",
        hover_name="region",
        animation_frame="date",  # 👈 Now it will show the slider
        color_continuous_scale="Reds",
        title="Excess Deaths Over Time"
    )

    map_path = os.path.join(current_app.static_folder, 'map_plot.html')
    if os.path.exists(map_path):
        os.remove(map_path)
    fig.write_html(map_path)

    return render_template('result.html', plot_url='map_plot.html')



