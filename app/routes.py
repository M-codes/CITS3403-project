from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

from app import db
from app.models import DataPoint
from app.models import SharedPlot

bp = Blueprint('main', __name__)

@bp.route('/home')
def index():
    return render_template("index.html")

@bp.route('/data_table')
def data_table():
    if 'user_id' not in session:
        flash("Please log in to view your data.", 'warning')
        return redirect(url_for('auth.home'))
    
    data = DataPoint.query.filter_by(user_id=session['user_id']).order_by(DataPoint.date.desc()).all()
    return render_template('data_table.html', data=data)


@bp.route('/upload_page')
def upload_page():
    return render_template("upload.html")

@bp.route('/forum')
def forum():
    posts = SharedPlot.query.order_by(SharedPlot.id.desc()).all()
    return render_template("forum.html", posts=posts)


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
            # Convert the date string to a datetime object
            date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Change format as needed
            value = float(value)
            lower = float(lower) if lower else None
            upper = float(upper) if upper else None
            confirmed = float(confirmed) if confirmed else None
        except ValueError:
            flash("Invalid numeric input or date format.", 'manual_entry:error')
            return redirect(url_for('main.manual_entry'))

        if region and date and pd.notnull(value):
            exists = DataPoint.query.filter_by(region=region, date=date, user_id=session['user_id']).first()
            if not exists:
                point = DataPoint(
                    region=region,
                    date=date,  # Save the date as a datetime.date object
                    value=value,
                    lower_bound=lower,
                    upper_bound=upper,
                    confirmed_deaths=confirmed,
                    user_id=session['user_id'] 
                )
                db.session.add(point)
                db.session.commit()
                flash(f"Data for {region} on {date_str} added successfully.", 'manual_entry:success')
                return redirect(url_for('main.manual_entry'))
            else:
                flash("Data point already exists.", 'manual_entry:warning')
                return redirect(url_for('main.manual_entry'))
        flash("Missing or invalid input.", 'manual_entry:error')
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

        all_data = []

        try:
            chunk_iter = pd.read_csv(filepath, chunksize=1000)

            for chunk in chunk_iter:
                for _, row in chunk.iterrows():
                    region = row.get("Entity")
                    date_str = row.get("Day")
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        continue

                    value = row.get("Cumulative excess deaths per 100,000 people (central estimate)")
                    lower = row.get("Cumulative excess deaths per 100,000 people (95% CI, lower bound)")
                    upper = row.get("Cumulative excess deaths per 100,000 people (95% CI, upper bound)")
                    confirmed = row.get("Total confirmed deaths due to COVID-19 per 100,000 people")

                    if pd.notnull(value):
                        exists = DataPoint.query.filter_by(region=region, date=date).first()
                        if not exists:
                            dp = DataPoint(
                                region=region,
                                date=date,
                                value=value,
                                lower_bound=lower,
                                upper_bound=upper,
                                confirmed_deaths=confirmed,
                                user_id=session['user_id']
                            )
                            db.session.add(dp)

                        all_data.append({
                            "Entity": region,
                            "Day": date,
                            "Cumulative excess deaths per 100,000 people (central estimate)": value,
                            "Cumulative excess deaths per 100,000 people (95% CI, lower bound)": lower,
                            "Cumulative excess deaths per 100,000 people (95% CI, upper bound)": upper,
                            "Total confirmed deaths due to COVID-19 per 100,000 people": confirmed
                        })

            db.session.commit()

        except Exception as e:
            flash("Failed to read or process CSV file.", 'upload:error')
            return redirect(url_for('main.upload_page'))

        if not all_data:
            flash("No usable data found in the file.", 'upload:warning')
            return redirect(url_for('main.upload_page'))

        # After the upload, let's base the plot on the entire user's data (from the DB)
        user_data = DataPoint.query.filter_by(user_id=session['user_id']).all()

        # Convert the data to DataFrame for plotting
        df_plot = pd.DataFrame([{
            "Entity": dp.region,
            "Day": dp.date,
            "Cumulative excess deaths per 100,000 people (central estimate)": dp.value,
            "Cumulative excess deaths per 100,000 people (95% CI, lower bound)": dp.lower_bound,
            "Cumulative excess deaths per 100,000 people (95% CI, upper bound)": dp.upper_bound,
            "Total confirmed deaths due to COVID-19 per 100,000 people": dp.confirmed_deaths
        } for dp in user_data])

        # --- Create the Map ---
        fig_map = px.choropleth(
            df_plot,
            locations="Entity",
            locationmode="country names",
            color="Cumulative excess deaths per 100,000 people (central estimate)",
            hover_name="Entity",
            animation_frame="Day", 
            hover_data={
                "Cumulative excess deaths per 100,000 people (95% CI, lower bound)": True,
                "Cumulative excess deaths per 100,000 people (95% CI, upper bound)": True,
                "Total confirmed deaths due to COVID-19 per 100,000 people": True
            },
            color_continuous_scale="Reds",
            title="Cumulative Excess Deaths per 100,000 People (Central Estimate)"
        )
        map_path = os.path.join(current_app.static_folder, 'plots', 'map_plot.html')
        fig_map.write_html(map_path)

        # --- Create the Time Series ---
        df_plot['Day'] = pd.to_datetime(df_plot['Day'])
        fig_line = px.line(
            df_plot,
            x='Day',
            y='Cumulative excess deaths per 100,000 people (central estimate)',
            title="Excess Deaths Over Time",
            labels={'Day': 'Date', 'Cumulative excess deaths per 100,000 people (central estimate)': 'Excess Deaths per 100,000 People'},
            line_shape='linear'
        )

        # Add a dropdown filter for country
        fig_line.update_layout(
            updatemenus=[{
                'buttons': [
                    {
                        'method': 'update',
                        'label': 'All Countries',
                        'args': [{'visible': [True] * len(fig_line.data)}, {'title': 'Excess Deaths Over Time (All Countries)'}]
                    }
                ] + [
                    {
                        'method': 'update',
                        'label': country,
                        'args': [
                            {'visible': [trace.name == country for trace in fig_line.data]},
                            {'title': f'Excess Deaths Over Time - {country}'}
                        ]
                    }
                    for country in df_plot['Entity'].dropna().unique()
                ],
                'direction': 'down',
                'showactive': True
            }]
        )
        time_series_path = os.path.join(current_app.static_folder, 'plots', 'time_series_plot.html')
        fig_line.write_html(time_series_path)

        # --- Pass both plots to the result page ---
        # Store latest uploaded data in session (or in temp DB if large)
        session['upload_success'] = True
        flash("Upload successful. Please select a graph to view.", "upload:success")
        return redirect(url_for('main.select_graph'))

    flash("Invalid file format. Please upload a CSV file.", 'upload:error')
    return redirect(url_for('main.upload_page'))

@bp.route('/select_graph', methods=['GET', 'POST'])
def select_graph():
    if not session.get('upload_success'):
        flash("Please upload data first.", "warning")
        return redirect(url_for('main.upload_page'))

    if request.method == 'POST':
        graph_type = request.form.get('graph_type')
        if graph_type == 'map':
            return redirect(url_for('main.map_view'))
        elif graph_type == 'line':
            return redirect(url_for('main.show_line_graph'))
        elif graph_type == 'bar':
            return redirect(url_for('main.show_bar_graph'))
        elif graph_type == 'pie':
            return redirect(url_for('main.show_pie_chart'))

    return render_template('select_graph.html')

@bp.route('/manage_data', methods=['GET', 'POST'])
def manage_data():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to manage your data.", "error")
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'clear_all':
            DataPoint.query.filter_by(user_id=user_id).delete()
            db.session.commit()
            flash("All your data has been cleared.", "success")
            return redirect(url_for('main.manage_data'))

        elif action == 'delete_one':
            dp_id = request.form.get('data_id')
            if dp_id and dp_id.isdigit():
                dp = DataPoint.query.filter_by(id=int(dp_id), user_id=user_id).first()
                if dp:
                    db.session.delete(dp)
                    db.session.commit()
                    flash("Record deleted.", "success")
                else:
                    flash("Record not found or unauthorized.", "warning")
            else:
                flash("Invalid record ID.", "error")

        return redirect(url_for('main.manage_data'))

    # GET: Show all user's data
    data = DataPoint.query.filter_by(user_id=user_id).all()
    return render_template('manage_data.html', data=data)



@bp.route('/map')
def map_view():
    selected_date = request.args.get('date')

    # If selected_date is None, use the current date as a fallback
    if not selected_date:
        selected_date = pd.to_datetime('today').strftime('%Y-%m-%d')  # Default to today's date

    try:
        selected_date = pd.to_datetime(selected_date)
    except Exception as e:
        flash("Invalid date format.", 'error')
        return redirect(url_for('main.index'))

    

    data = DataPoint.query.filter_by(user_id=session['user_id']).all()

    if not data:
        return "No data available.", 404

    # Convert the data to a DataFrame
    df = pd.DataFrame([{
        'region': dp.region,
        'date': dp.date,
        'value': dp.value
    } for dp in data])

    # Ensure 'date' column is in datetime format for Plotly compatibility
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # Drop rows with missing dates
    df = df.dropna(subset=['date'])

    # Sort the DataFrame by date to ensure proper animation order
    df = df.sort_values(by='date')

    # Create the choropleth with animation (date slider)
    fig = px.choropleth(
        df,
        locations="region",
        locationmode="country names",
        color="value",
        hover_name="region",
        animation_frame="date",  # Date slider will be generated
        color_continuous_scale="Reds",
        title=f"Excess Deaths on {selected_date.strftime('%Y-%m-%d')}",  # Use the formatted date
        range_color=[df['value'].min(), df['value'].max()]  # Ensures consistent color scale across all frames
    )

    # Save the plot as an HTML file
    map_path = os.path.join(current_app.static_folder, 'plots/map_plot.html')
    if os.path.exists(map_path):
        os.remove(map_path)
    fig.write_html(map_path)

    return render_template('result.html', plot_url='plots/map_plot.html')

@bp.route('/line_chart')
def show_line_graph():
    # Same code as your existing line chart generation
    return render_template('result.html', plot_url='plots/time_series_plot.html')

@bp.route('/bar_chart')
def show_bar_graph():
    # Example bar chart
    data = DataPoint.query.filter_by(user_id=session['user_id']).all()
    df = pd.DataFrame([{'region': d.region, 'value': d.value} for d in data])
    df = df.groupby('region').mean(numeric_only=True).reset_index()

    fig = px.bar(df, x='region', y='value', title="Average Excess Deaths by Region")
    path = os.path.join(current_app.static_folder, 'plots/bar_chart.html')
    fig.write_html(path)
    return render_template('result.html', plot_url='plots/bar_chart.html')


@bp.route('/pie_chart')
def show_pie_chart():
    data = DataPoint.query.filter_by(user_id=session['user_id']).all()

    # Convert to DataFrame
    df = pd.DataFrame([{'region': d.region, 'value': d.value} for d in data])

    # Group by region and sum the values
    df = df.groupby('region', as_index=False).sum(numeric_only=True)

    # Get Top 10 regions by total excess deaths
    df_top10 = df.sort_values(by='value', ascending=False).head(10)

    # Create pie chart
    fig = px.pie(
        df_top10,
        values='value',
        names='region',
        title='Top 10 Regions by Total Excess Deaths'
    )

    # Save plot
    path = os.path.join(current_app.static_folder, 'plots/pie_chart.html')
    fig.write_html(path)
    
    return render_template('result.html', plot_url='plots/pie_chart.html')

@bp.route('/upload_post', methods=['POST'])
def upload_post():
    if 'user_id' not in session:
        flash("Please log in to upload a post.", 'warning')
        return redirect(url_for('auth.login_page'))

    file = request.files.get('plot_image')
    comment = request.form.get('comment')
    email = request.form.get('email')

    if not file or not file.filename.endswith('.png'):
        flash("Please upload a valid PNG file.", 'error')
        return redirect(url_for('main.forum'))

    if not email or not comment:
        flash("Email and comment are required.", 'error')
        return redirect(url_for('main.forum'))

    # Save the file
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.static_folder, 'uploads', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)

    # Save to the database
    shared_plot = SharedPlot(
        plot_filename=f'uploads/{filename}',
        comment=comment,
        email=email,
        user_id=session['user_id']
    )
    db.session.add(shared_plot)
    db.session.commit()

    flash("Post uploaded successfully!", 'success')
    return redirect(url_for('main.forum'))


