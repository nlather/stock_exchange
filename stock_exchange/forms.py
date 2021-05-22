from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField , RadioField,TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from stock_exchange import get_api
from stock_exchange.dbmodels import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists!')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class QuoteForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Get Quote')

class BuyForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Buy Stocks')

class SellForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    submit = SubmitField('Sell Stocks')

class NewTransactionForm(FlaskForm) :
    transactionDesc = TextAreaField('Transaction Description' , validators=[DataRequired()]) 
    amount = IntegerField('Amount($)', validators=[DataRequired()])
    transactionType = RadioField('Transaction Type',choices=['Expense','Income'], default='Income')
    submit = SubmitField('Add Transaction')
