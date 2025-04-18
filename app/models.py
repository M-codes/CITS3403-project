from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app import db

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(100))
    date = db.Column(db.String(100))  # or db.Date if you're parsing it
    value = db.Column(db.Float)