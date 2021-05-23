from flask import render_template, url_for, flash, redirect
from stock_exchange import app, db, bcrypt, get_api
from stock_exchange.forms import RegistrationForm, LoginForm, QuoteForm, BuyForm, SellForm, NewTransactionForm
from stock_exchange.dbmodels import User, Stock, Log
from flask_login import login_user, current_user, logout_user, login_required
from flask_paginate import Pagination, get_page_args

def get_posts(offset, per_page, logs) :
    return logs[offset: offset+per_page]

@app.route("/")
@app.route("/home")
@login_required
def index():
    stocklist = current_user.stocks
    stocks = []
    total = 0
    for stock in stocklist:
        api_data = get_api(stock.symbol)['data']
        stocks.append({
            'company':api_data['companyName'],
            'symbol':api_data['symbol'],
            'amount':stock.amount,
            'price':f"{api_data['latestPrice']:.2f}",
            'total_price':f"{stock.amount*api_data['latestPrice']:.2f}"
        })
        total += stock.amount*api_data['latestPrice']
    return render_template('index.html',stocks=stocks, flag=bool(len(stocks) > 0), cash=f'{current_user.cash:.2f}', total=f'{total:.2f}', expenditure=f'{current_user.expenditure:.2f}', income=f'{current_user.income:.2f}')

@app.route("/history")
@login_required
def history():
    logs_list = current_user.logs
    logs=[]
    for log in logs_list :
        logs.append({
            'datetime': log.datetime,
            'log_type':log.log_type,
            'desc':log.description
            })
        # print(log.log_type + '->>>' + log.stock_info)
    page,per_page,offset= get_page_args(page_parameter='page',per_page_parameter='per_page')
    per_page=10
    total_logs=len(logs)
    
    pagination_logs= get_posts(offset=offset, per_page=per_page, logs=logs)
    paginationLog= Pagination(page=page,per_page=per_page, total=total_logs, css_framework='bootstrap4')
    
    return render_template('history.html', flag = bool(len(logs) > 0), logs=pagination_logs, paginationLog=paginationLog,page=page,per_page=per_page)

@app.route("/quote", methods=['GET', 'POST'])
def quote():
    form = QuoteForm()
    if form.validate_on_submit():
        api_data = get_api(form.symbol.data)
        if api_data['status'] != 200:
            flash('Invalid Symbol!', 'danger')
        else:
            data = api_data['data']
            flash(f"A share of {data['symbol']} ({data['companyName']}) costs ${data['latestPrice']:.2f}", 'success')
        return redirect(url_for('quote'))
    return render_template('quote.html', form=form)

@app.route("/buy", methods=['GET', 'POST'])
@login_required
def buy():
    form = BuyForm()
    if form.validate_on_submit():
        api_data = get_api(form.symbol.data)
        if api_data['status'] != 200:
            flash('Invalid Symbol!', 'danger')
        elif api_data['data']['latestPrice']*form.amount.data > current_user.cash:
            flash('You don\'t have enough cash!', 'danger')
        else:
            price = api_data['data']['latestPrice']*form.amount.data
            symbol = api_data['data']['symbol']
            current_user.cash -= price
            current_user.expenditure += price
            stock = Stock.query.filter_by(owner=current_user, symbol=symbol).first()
            if stock:
                stock.amount += form.amount.data
            else:
                stock = Stock(owner=current_user, symbol=symbol, amount=form.amount.data)
                db.session.add(stock)
            log = Log(owner=current_user, log_type='Expense', description=f"Bought {form.amount.data} shares of {symbol} for ${price:.2f}")
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('index'))
    return render_template('buy.html', form=form)

@app.route("/new", methods=['GET', 'POST'])
@login_required
def new():
    form = NewTransactionForm()
    if form.validate_on_submit():
        amount=form.amount.data
        ttype=form.transactionType.data
        if ttype=="Expense" and amount>current_user.cash :
            flash('You don\'t have enough cash!', 'danger')
        else :
            if ttype=="Income" :
                current_user.cash+=amount
                current_user.income+=amount
            else :
                current_user.cash-=amount
                current_user.expenditure+=amount
            log=Log(owner=current_user, log_type=form.transactionType.data, description=f"{ttype} of ${form.amount.data} : {form.transactionDesc.data}")
            db.session.add(log)
            db.session.commit()
            flash(f'Successfully Added the transaction under the {form.transactionType.data} category' ,'success')
            return redirect(url_for('index'))
    return render_template('new.html', form=form)

@app.route("/sell", methods=['GET', 'POST'])
@login_required
def sell():
    form = SellForm()
    if form.validate_on_submit():
        api_data = get_api(form.symbol.data)
        if api_data['status'] != 200:
            flash('Invalid Symbol!', 'danger')
        else:
            price = api_data['data']['latestPrice']*form.amount.data
            symbol = api_data['data']['symbol']
            stock = Stock.query.filter_by(owner=current_user, symbol=symbol).first()
            if stock and stock.amount >= form.amount.data:
                current_user.cash += price
                current_user.income += price
                stock.amount -= form.amount.data
                if stock.amount == 0:
                    db.session.delete(stock)
                log = Log(owner=current_user, log_type='Income', description=f"Sold {form.amount.data} shares of {symbol} for ${price:.2f}")
                db.session.add(log)
                db.session.commit()
                return redirect(url_for('index'))
            else:
                flash(f"You don't have sufficient stocks of {symbol}", 'danger')
    return render_template('sell.html', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful! Please check username and password!', 'danger')
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
