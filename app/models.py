from . import db


class WorkHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    hours = db.Column(db.Float, nullable=False)


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hourly_rate = db.Column(db.Float, default=150)
    password = db.Column(db.String(100), default='password123')
