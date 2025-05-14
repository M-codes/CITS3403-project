from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
 # or wherever User is defined
from app import db
from datetime import datetime

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))
    date = db.Column(db.Date)  # Changed to db.Date
    value = db.Column(db.Float)  # The inputted value
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # NEW: Add foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='datapoints')

class SharedPlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plot_filename = db.Column(db.String(255), nullable=False)  # Path to the .png file
    comment = db.Column(db.Text, nullable=True)  # Optional comment
    email = db.Column(db.String(120), nullable=False)  # Email of the user sharing the plot
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Associated user
    title = db.Column(db.String(100), nullable=True)
    user = db.relationship('User', backref='shared_plots', lazy=True)

class DataShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_id = db.Column(db.Integer, db.ForeignKey('data_point.id'), nullable=False)
    shared_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='shared_out')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='shared_in')
    data_point = db.relationship('DataPoint', backref='shares')