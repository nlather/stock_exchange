import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_KEY = os.environ.get('API_KEY')
print(API_KEY)
def get_api(symbol):
    response = requests.get(f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={API_KEY}')
    if response.status_code != 200:
        return {'status': response.status_code, 'data':''}
    return {'status': response.status_code, 'data':response.json()}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from stock_exchange import routes
