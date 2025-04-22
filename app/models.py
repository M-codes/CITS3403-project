from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app import db

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))
    date = db.Column(db.String(100))  # or use db.Date
    value = db.Column(db.Float)  # Central estimate
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    confirmed_deaths = db.Column(db.Float)