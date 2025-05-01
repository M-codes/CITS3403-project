from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from app.auth import User  # or wherever User is defined
from app import db

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))
    date = db.Column(db.Date)  # Changed to db.Date
    value = db.Column(db.Float)  # Central estimate
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    confirmed_deaths = db.Column(db.Float)
    # NEW: Add foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='datapoints')

class SharedPlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plot_filename = db.Column(db.String(255), nullable=False)  # Path to the .png file
    comment = db.Column(db.Text, nullable=True)  # Optional comment
    email = db.Column(db.String(120), nullable=False)  # Email of the user sharing the plot
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Associated user

    user = db.relationship('User', backref='shared_plots', lazy=True)
