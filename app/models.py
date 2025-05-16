from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
from app import db
from datetime import datetime, UTC

# User model: stores the user credentials
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) #unique user id
    email = db.Column(db.String(120), unique=True, nullable=False) #user email must be unique so no duplicates
    password_hash = db.Column(db.String(128), nullable=False) #hashed password

# Stores the users uploaded data set, or entries that are manually made.
class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True) #each data point has a unique ID
    region = db.Column(db.String(100)) #region or coutnry name
    date = db.Column(db.Date)  # Date of the data point
    value = db.Column(db.Float)  # Value for the data point (e.g., cases)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC)) # Timestamp of creation
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Reference to uploader (FK, so ties it the userid)

    user = db.relationship('User', backref='datapoints') # Relationship to User

# SharedPlot model: stores plots shared to the forum
class SharedPlot(db.Model):
    id = db.Column(db.Integer, primary_key=True) # plot id
    plot_filename = db.Column(db.String(255), nullable=True)    # Path to the .png file (optional)
    plot_html = db.Column(db.Text, nullable=True)               # NEW: HTML content of the plot
    comment = db.Column(db.Text, nullable=True)                 # optional user comment (caption)
    email = db.Column(db.String(120), nullable=False)           # the email of the user who uploaded it 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Reference to user
    title = db.Column(db.String(100), nullable=True)  # Optional plot title
    user = db.relationship('User', backref='shared_plots', lazy=True)  # Relationship to User
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))  # Timestamp of sharing

# DataShare model: tracks sharing of data points between users
class DataShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique share ID
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who shared the data
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who received the data
    data_id = db.Column(db.Integer, db.ForeignKey('data_point.id'), nullable=False)  # Shared data point
    shared_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))  # Timestamp of sharing

    owner = db.relationship('User', foreign_keys=[owner_id], backref='shared_out')  # owner relationship
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='shared_in')  # Recipient relationship
    data_point = db.relationship('DataPoint', backref='shares')  # DataPoint relationship