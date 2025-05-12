from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

from app import db
from app.models import DataPoint,DataShare, User
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

    # 1) Your own DataPoints
    my_data = (
        DataPoint.query
        .filter_by(user_id=session['user_id'])
        .order_by(DataPoint.date.desc())
        .all()
    )

    # 2) All DataShares _to_ you
    shared_shares = (
        DataShare.query
        .filter_by(recipient_id=session['user_id'])
        .join(DataPoint, DataShare.data_id == DataPoint.id)
        .join(User,     DataShare.owner_id == User.id)
        .options(
            db.contains_eager(DataShare.data_point),
            db.contains_eager(DataShare.owner)
        )
        .order_by(DataShare.shared_at.desc())
        .all()
    )

    # DEBUG: print out what we fetched
    print("SHARED SHARES:", [(s.owner.email, s.data_point.id) for s in shared_shares])

    return render_template(
        'data_table.html',
        my_data=my_data,
        shared_shares=shared_shares
    )


@bp.route('/upload_page')
def upload_page():
    return render_template("upload.html")

@bp.route('/forum')
def forum():
    posts = SharedPlot.query.order_by(SharedPlot.id.desc()).all()
    return render_template("forum.html", posts=posts)

@bp.route('/delete_datapoint/<int:data_id>', methods=['POST'])
def delete_datapoint(data_id):
    if 'user_id' not in session:
        flash("You must be logged in to delete data.", "error")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    dp = DataPoint.query.filter_by(id=data_id, user_id=user_id).first()
    if not dp:
        flash("Data not found or unauthorized.", "warning")
        return redirect(url_for('main.manage_data'))

    # First delete related shares (if any)
    DataShare.query.filter_by(data_id=data_id).delete()

    # Now delete the data point
    db.session.delete(dp)
    db.session.commit()

    flash("Data point and all related shares deleted.", "success")
    return redirect(url_for('main.manage_data'))

@bp.route('/manual_entry', methods=['GET', 'POST'])
def manual_entry():
    # ——— LOGIN GUARD ———
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.login'))

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
                date=date,
                value=value,
                lower_bound=lower,
                upper_bound=upper,
                confirmed_deaths=confirmed,
                user_id=session['user_id']
            )
            db.session.add(point)
            db.session.commit()
            flash(f"Data for {region} on {date_str} added successfully.", 'manual_entry:success')
        else:
            flash("Data point already exists.", 'manual_entry:warning')

        return redirect(url_for('main.manual_entry'))

    # GET: build your country list scoped to this user
    country_list = [
        row[0]
        for row in (
            db.session
              .query(DataPoint.region)
              .filter_by(user_id=session['user_id'])
              .distinct()
              .order_by(DataPoint.region)
              .all()
        )
    ]
    return render_template('manual_entry.html', countries=country_list)
    
@bp.route('/upload', methods=['POST'])
def upload():
    # ——— LOGIN GUARD ———
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    file = request.files.get('file')
    if not (file and file.filename.endswith('.csv')):
        flash("Invalid file format. Please upload a CSV file.", 'upload:error')
        return redirect(url_for('main.upload_page'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    all_data = []
    try:
        # Read the first chunk to validate the structure
        first_chunk = pd.read_csv(filepath, nrows=1)
        required_columns = {"Entity", "Day"}
        if not required_columns.issubset(first_chunk.columns):
            flash("CSV must contain 'Entity' and 'Day' columns.", 'upload:error')
            return redirect(url_for('main.upload_page'))

        # Identify the dynamic data column (must be exactly one additional column)
        data_columns = [col for col in first_chunk.columns if col not in required_columns]
        if len(data_columns) != 1:
            flash("CSV must contain exactly one additional data column.", 'upload:error')
            return redirect(url_for('main.upload_page'))

        data_column = data_columns[0]  # The dynamic column name
        session['data_column'] = data_column  # Store it in the session for later use

        # Process the file in chunks
        for chunk in pd.read_csv(filepath, chunksize=1000):
            for _, row in chunk.iterrows():
                # parse region, date, values...
                region = row["Entity"]
                date = pd.to_datetime(row["Day"], errors='coerce').date()
                if pd.isna(date):
                    continue

                value = row[data_column]

                # Check for duplicates
                exists = DataPoint.query.filter_by(
                    region=region,
                    date=date,
                    user_id=session['user_id']
                ).first()

                if not exists and pd.notnull(value):
                    dp = DataPoint(
                        region=region,
                        date=date,
                        value=value,
                        user_id=session['user_id']
                    )
                    db.session.add(dp)

                all_data.append({
                    "region": region,
                    "date": date,
                    "value": value
                })
        db.session.commit()
    except Exception as e:
        flash(f"Failed to read or process CSV file: {str(e)}", 'upload:error')
        return redirect(url_for('main.upload_page'))

    if not all_data:
        flash("No usable data found in the file.", 'upload:warning')
        return redirect(url_for('main.upload_page'))

    flash(f"Upload successful. Data column '{data_column}' detected. Please select a graph to view.", "upload:success")
    return redirect(url_for('main.select_graph'))

@bp.route('/select_graph', methods=['GET', 'POST'])
def select_graph():
    if not session.get('upload_success'):
        flash("Please upload data first.", "warning")
        return redirect(url_for('main.upload_page'))

    if request.method == 'POST':
        graph_type = request.form.get('graph_type')
        date = request.form.get('date')

        if graph_type == 'map':
            return redirect(url_for('main.map_view'))
        elif graph_type == 'line':
            return redirect(url_for('main.show_line_graph'))
        elif graph_type == 'bar':
            return redirect(url_for('main.show_bar_graph', date=date))
        elif graph_type == 'pie':
            return redirect(url_for('main.show_pie_chart', date=date))

    # 👇 Get distinct dates
    all_dates = (
        db.session.query(DataPoint.date)
        .filter_by(user_id=session['user_id'])
        .distinct()
        .order_by(DataPoint.date)
        .all()
    )
    unique_dates = [d[0] for d in all_dates]  # d is a tuple like ('2021-05-01',)

    return render_template('select_graph.html', available_dates=unique_dates)

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

    # Dynamic title based on the uploaded data column
    data_column = session.get('data_column', 'Data')
    title = f"{data_column} on {selected_date.strftime('%Y-%m-%d')}"

    # Create the choropleth with animation (date slider)
    fig = px.choropleth(
        df,
        locations="region",
        locationmode="country names",
        color="value",
        hover_name="region",
        animation_frame="date",  # Date slider will be generated
        color_continuous_scale="Reds",
        title=title,
        range_color=[df['value'].min(), df['value'].max()] #Ensures consistant colour scale across all frmaes
    )

    # Save the plot as an HTML file
    map_path = os.path.join(current_app.static_folder, 'plots/map_plot.html')
    if (os.path.exists(map_path)):
        os.remove(map_path)
    fig.write_html(map_path)

    return render_template('result.html', plot_url='plots/map_plot.html',plot_type='map')

@bp.route('/line_chart')
def show_line_graph():
    # Same code as your existing line chart generation
    return render_template('result.html', plot_url='plots/time_series_plot.html',plot_type='line')

@bp.route('/bar_chart')
def show_bar_graph():
    selected_date = request.args.get('date')  # Expecting 'YYYY-MM-DD'
    
    query = DataPoint.query.filter_by(user_id=session['user_id'])
    if selected_date:
        query = query.filter_by(date=selected_date)

    data = query.all()
    df = pd.DataFrame([{'region': d.region, 'value': d.value} for d in data])

    if df.empty:
        flash("No data available for the selected date.", "warning")
        return redirect(url_for('main.select_graph'))

    df = df.groupby('region').mean(numeric_only=True).reset_index()

    # Dynamic title based on the uploaded data column
    data_column = session.get('data_column', 'Data')
    title = f"{data_column} by Region ({selected_date})"

    fig = px.bar(df, x='region', y='value', title=title)
    path = os.path.join(current_app.static_folder, 'plots/bar_chart.html')
    fig.write_html(path)
    
    return render_template('result.html', plot_url='plots/bar_chart.html', plot_type='bar')



@bp.route('/pie_chart')
def show_pie_chart():
    selected_date = request.args.get('date')  # Expecting 'YYYY-MM-DD'

    query = DataPoint.query.filter_by(user_id=session['user_id'])
    if selected_date:
        query = query.filter_by(date=selected_date)

    data = query.all()
    df = pd.DataFrame([{'region': d.region, 'value': d.value} for d in data])

    if df.empty:
        flash("No data available for the selected date.", "warning")
        return redirect(url_for('main.select_graph'))

    df = df.groupby('region', as_index=False).sum(numeric_only=True)
    df_top10 = df.sort_values(by='value', ascending=False).head(10)

    # Dynamic title based on the uploaded data column
    data_column = session.get('data_column', 'Data')
    title = f"Top 10 Regions for {data_column} ({selected_date})"

    fig = px.pie(
        df_top10,
        values='value',
        names='region',
        title=title
    )

    path = os.path.join(current_app.static_folder, 'plots/pie_chart.html')
    fig.write_html(path)
    
    return render_template('result.html', plot_url='plots/pie_chart.html', plot_type='pie')


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

@bp.route('/share_data', methods=['GET', 'POST'])
def share_data():
    if 'user_id' not in session:
        flash('Please log in to share data.', 'warning')
        return redirect(url_for('auth.login'))

    owner_id = session['user_id']
    # Load existing users for dropdown
    users = User.query.filter(User.id != owner_id).order_by(User.email).all()
    # Load owner's data items
    data_points = DataPoint.query.filter_by(user_id=owner_id).order_by(DataPoint.date.desc()).all()

    if request.method == 'POST':
        recipient_email = request.form.get('recipient_email')
        selected_ids = request.form.getlist('data_ids')  # list of data_point.id strings

        if not recipient_email or not selected_ids:
            flash('Select a user and at least one data item.', 'error')
            return redirect(url_for('main.share_data'))

        recipient = User.query.filter_by(email=recipient_email).first()
        if not recipient:
            flash('User not found.', 'error')
            return redirect(url_for('main.share_data'))

        # Create share records
        for dp_id in selected_ids:
            # avoid duplicates
            exists = DataShare.query.filter_by(
                owner_id=owner_id,
                recipient_id=recipient.id,
                data_id=int(dp_id)
            ).first()
            if not exists:
                share = DataShare(
                    owner_id=owner_id,
                    recipient_id=recipient.id,
                    data_id=int(dp_id)
                )
                db.session.add(share)
        db.session.commit()
        flash(f"Shared {len(selected_ids)} items with {recipient.email}.", 'success')
        return redirect(url_for('main.share_data'))

    return render_template(
        'share_data.html',
        users=users,
        data_points=data_points
    )

def get_shared_datapoints(user_id, owner_id=None):
    query = (
        DataShare.query
        .filter(DataShare.recipient_id == user_id)
    )
    if owner_id:
        query = query.filter(DataShare.owner_id == owner_id)
    shares = (
        query
        .join(DataPoint, DataShare.data_id == DataPoint.id)
        .with_entities(
            DataPoint.id,
            DataPoint.region,
            DataPoint.date,
            DataPoint.value
        )
        .all()
    )
    return [
        {"id": d.id, "region": d.region, "date": d.date, "value": d.value}
        for d in shares
    ]

@bp.route('/select_shared_graph', methods=['GET', 'POST'])
def select_shared_graph():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # fetch distinct sharers
    sharers = (
        User.query
        .join(DataShare, User.id == DataShare.owner_id)
        .filter(DataShare.recipient_id == user_id)
        .with_entities(User.id, User.email)
        .distinct()
        .all()
    )

    if request.method == 'POST':
        graph_type = request.form['graph_type']
        date       = request.form.get('date')
        sharer_id  = request.form.get('sharer_id')
        # build endpoint with sharer filter
        endpoint = 'main.shared_map_view' if graph_type=='map' else f"main.show_shared_{graph_type}"
        return redirect(url_for(endpoint, date=date, sharer_id=sharer_id))

    # build a list of distinct dates from shared data
    shared = get_shared_datapoints(user_id)
    dates = sorted({d['date'] for d in shared})
    return render_template(
        'select_shared_graph.html',
        available_dates=dates,
        sharers=sharers
    )


@bp.route('/map')
def shared_map_view():
    user_id = session['user_id']
    date_str = request.args.get('date')
    sharer_id = request.args.get('sharer_id', type=int)

    df = pd.DataFrame(get_shared_datapoints(user_id, owner_id=sharer_id))
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values(by='date')

    title = f"Shared Data from user #{sharer_id}: Excess Deaths {date_str}"
    fig = px.choropleth(
        df,
        locations="region",
        locationmode="country names",
        color="value",
        hover_name="region",
        animation_frame="date",
        title=title,
        range_color=[df['value'].min(), df['value'].max()]
    )
    path = os.path.join(current_app.static_folder, 'plots', 'shared_map.html')
    fig.write_html(path)
    return render_template('result.html', plot_url='plots/shared_map.html', plot_type='map')

@bp.route('/line')
def show_shared_line():
    user_id = session['user_id']
    sharer_id = request.args.get('sharer_id', type=int)
    df = pd.DataFrame(get_shared_datapoints(user_id, owner_id=sharer_id))
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    fig = px.line(df, x='date', y='value', color='region', title='Shared Data: Time Series')
    path = os.path.join(current_app.static_folder, 'plots', 'shared_time_series_plot.html')
    fig.write_html(path)
    return render_template('result.html', plot_url='plots/shared_time_series_plot.html', plot_type='line')


@bp.route('/bar')
def show_shared_bar():
    user_id = session['user_id']
    sharer_id = request.args.get('sharer_id', type=int)
    date_str = request.args.get('date')
    df = pd.DataFrame(get_shared_datapoints(user_id, owner_id=sharer_id))
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if date_str:
        df = df[df['date'] == pd.to_datetime(date_str)]
    df = df.groupby('region', as_index=False).mean(numeric_only=True)
    fig = px.bar(df, x='region', y='value', title=f"Shared: Avg Excess Deaths ({date_str})")
    path = os.path.join(current_app.static_folder, 'plots', 'shared_bar.html')
    fig.write_html(path)
    return render_template('result.html', plot_url='plots/shared_bar.html', plot_type='bar')


@bp.route('/pie')
def show_shared_pie():
    user_id = session['user_id']
    sharer_id = request.args.get('sharer_id', type=int)
    date_str = request.args.get('date')
    df = pd.DataFrame(get_shared_datapoints(user_id, owner_id=sharer_id))
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if date_str:
        df = df[df['date'] == pd.to_datetime(date_str)]
    df = df.groupby('region', as_index=False).sum(numeric_only=True)
    df_top10 = df.nlargest(10, 'value')
    fig = px.pie(df_top10, values='value', names='region', title=f"Shared: Top 10 Excess Deaths ({date_str})")
    path = os.path.join(current_app.static_folder, 'plots', 'shared_pie.html')
    fig.write_html(path)
    return render_template('result.html', plot_url='plots/shared_pie.html', plot_type='pie')
