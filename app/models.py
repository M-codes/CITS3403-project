from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class DataPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(64))
    date = db.Column(db.String(64))  # Or db.Date if you parse it
    value = db.Column(db.Float)