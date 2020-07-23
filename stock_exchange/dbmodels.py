from stock_exchange import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cash = db.Column(db.Float, nullable=False, default=10000)
    stocks = db.relationship('Stock', backref='owner', lazy=True)
    logs = db.relationship('Log', backref='owner', lazy=True)

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone(timedelta(hours=5, minutes=30))))
    stock_info = db.Column(db.String(60), nullable=False)
    log_type = db.Column(db.String(6), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
