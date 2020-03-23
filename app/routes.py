from app import app, hashing, db, login
from flask import make_response, redirect, render_template, request, flash, url_for
from app.forms import RegistrationForm, LoginForm, ChompForm, SearchForm
from app.models import User, Chomp
import secrets
import time
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from flask_login import login_user, current_user, logout_user
import urllib
import os
from hashlib import sha512, md5
import requests
import string as string_func
import random

class ChompHolder:
    def __init__(self, username, body):
        self.username = username
        self.body = body

def get_most_recent_chomps():
    chompers = []
    chomps = Chomp.query.order_by(text('id desc'))
    for chomp in chomps:
        user = User.query.filter_by(id=chomp.user_id).first()
        username = user.username
        body = chomp.body
        recent_chomp = ChompHolder(username=username, body=body)
        chompers.append(recent_chomp)

    return chompers

def get_user_w_id(id):
    try:
        return User.query.filter_by(id=id).first()
    except Exception as e:
        return None

def user_exists(username):
    user = User.query.filter_by(username=username).first()
    return False if user is None else True

def is_username_valid(username, errors):
    return_val = None
    if len(username) >= 6:
        if not user_exists(username):
            return_val = True
        else:
            errors.append('That username is already taken')
            return_val = False
    else:
        errors.append('That username is too short')
        return_val = False

    return return_val, errors


def are_passwords_valid(password1, password2, errors):
    return_val = None
    if len(password1) >= 6:
        if password1 == password2:
            return_val = True
        else:
            errors.append('Passwords do not match')
            return_val = False
    else:
        errors.append('password is too short')
        return_val = False

    return return_val, errors


def hash_password(raw_pwd, salt):
    raw_pwd += app.config['PEPPER']
    return hashing.hash_value(raw_pwd, salt=salt)


def check_password(hash, raw, salt):
    return hash_password(raw, salt) == hash


def create_salt():
    return secrets.token_bytes(8)

@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@app.route('/')
@app.route('/index')
def index():
    if not request.cookies.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect('/dashboard')

@app.route('/secure/index')
def secure_index():
    return render_template('index.html')

@app.route('/register', methods=['get', 'post'])
def register():
    if request.cookies.get('logged_in') != None:
        print('logged in')
        return redirect('/dashboard')
    else:
        print('Not logged in')

    form = RegistrationForm()
    errors = []

    if form.validate_on_submit():
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        image = form.image.data
        tagline = form.tagline.data

        passwords_valid, errors = are_passwords_valid(password1, password2, errors)
        username_valid, errors = is_username_valid(username, errors)

        if username_valid and passwords_valid:
            salt = create_salt()
            password_hash = hash_password(password1, salt=salt)
            new_user = User(username=username, password_hash=password_hash, salt=salt, \
                            image=image, first_name=first_name, last_name=last_name,\
                            tagline=tagline)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/login')
        else:
            print(errors)
    return render_template('register.html', form=form, errors=errors)

@app.route('/secure/register', methods=['get', 'post'])
def secure_register():
    if current_user.is_authenticated:
        return redirect('/secure/dashboard')

    form = RegistrationForm()
    errors = []

    if form.validate_on_submit():
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        image = form.image.data
        tagline = form.tagline.data


        if image == "" or image == None or "onerror" in image:
            image = 'https://img.favpng.com/17/7/13/computer-icons-icon-design-user-png-favpng-uXME5zjHwHTJNs2Kzf5LvgFDR.jpg'

        passwords_valid, errors = are_passwords_valid(password1, password2, errors)
        username_valid, errors = is_username_valid(username, errors)

        if username_valid and passwords_valid:
            salt = create_salt()
            password_hash = hash_password(password1, salt=salt)
            new_user = User(username=username, password_hash=password_hash, salt=salt, \
                            image=image, first_name=first_name, last_name=last_name,\
                            tagline=tagline)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/secure/login')
        else:
            print(errors)
    return render_template('register.html', form=form, errors=errors)



@app.route('/login', methods=['get', 'post'])
def login():
    print(request.cookies.get('logged_in'))
    if request.cookies.get('logged_in') != None:
        print('logged in')
        return redirect('/dashboard')
    else:
        print('Not logged in')

    form = LoginForm()

    username = form.username.data
    password = form.password.data
    remember_me = form.remember_me.data

    if form.validate_on_submit():
        if user_exists(username):
            user = User.query.filter_by(username=username).first()
            if hash_password(password, user.salt) == user.password_hash:
                print('Successfully logged in')
                res = make_response(redirect(('/dashboard')))
                res.set_cookie('logged_in', 'True', max_age=60 * 60 * 24 * 365 * 2)
                res.set_cookie('user_id', str(user.id), max_age=60 * 60 * 24 * 365 * 2)
                return res
            else:
                flash('Invalid login credentials')
                redirect(('/login'))
        else:
            flash('Invalid login credentials')
            redirect('/login')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['get'])
def logout():
    res = make_response(redirect('/index'))
    res.set_cookie('logged_in', '-1', max_age=0)
    res.set_cookie('user_id', '-1', max_age=0)
    print('Successfully logged out')
    return res


@app.route('/dashboard', methods=['get', 'post'])
def dashboard():
    if request.cookies.get('logged_in') != None:
        user = get_user_w_id(request.cookies.get('user_id'))
        chomps = get_most_recent_chomps()
        return render_template('dashboard.html', user=user, form=ChompForm(), chomps=chomps)
    else:
        return redirect('/login')


@app.route('/chomp', methods=['get', 'post'])
def new_chomp():
    if request.cookies.get('logged_in') != None:
        if request.method == 'GET':
            user = request.args.get('user_id')
            chomp = request.args.get('body')

            if user != None and chomp != None:
                chomp = Chomp(user_id=user, body=chomp)
                db.session.add(chomp)
                db.session.commit()
                print('chomped')
            else:
                print('None :(')
            return redirect('/dashboard')
        elif request.method == 'POST':
            print('you posted')
            return redirect('/dashboard')
    else:
        print('idk what you did')
        return redirect('/dashboard')

@app.route('/process', methods=['post', ])
def process():
    if request.cookies.get('logged_in') != None:
        form = ChompForm()
        if form.validate_on_submit():
            user = request.cookies.get('user_id')
            body = form.body.data
            return redirect(url_for('new_chomp', user_id=user, body=body))
        return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/search', methods=['get', 'post'])
def search():
    if request.cookies.get('logged_in') != None:
        user = User.query.filter_by(id=request.cookies.get('user_id')).first()
        form = SearchForm()

        if form.validate_on_submit():
            username = form.username.data
            engine = create_engine('sqlite:///app.db')
            with engine.connect() as conn:
                rs = conn.execute("SELECT * FROM user WHERE username='{}'".format(username))
                usernames = []
                for item in rs:
                    usernames.append(item[1])
            return render_template('search.html', form=form, results=usernames, user=user)
        else:
            return render_template('search.html', form=form, user=user)
    else:
        return redirect('/login')

@app.route('/secure/login', methods=['get', 'post'])
def secure_login():
    form = LoginForm()

    username = form.username.data
    password = form.password.data
    remember_me = form.remember_me.data

    if form.validate_on_submit():
        if user_exists(username):
            user = User.query.filter_by(username=username).first()
            if hash_password(password, user.salt) == user.password_hash:
                login_user(user)
                return redirect(url_for('secure_dashboard'))
            else:
                flash('Invalid login credentials')
                redirect(('/seucre/login'))
        else:
            flash('Invalid login credentials')
            redirect('/secure/login')
    return render_template('login.html', form=form)


@app.route('/secure/dashboard', methods=['get', 'post'])
def secure_dashboard():
    if current_user.is_authenticated:
        return render_template('secure_dashboard.html', \
                               form=ChompForm(), chomps=get_most_recent_chomps())
    else:
        return redirect('/secure/login')

@app.route('/secure/process', methods=['post'])
def secure_process():
    form = ChompForm()

    if form.validate_on_submit():
        user_id = current_user.id
        body = form.body.data
        new_chomp = Chomp(user_id=user_id, body=body)
        db.session.add(new_chomp)
        db.session.commit()
    return redirect('/secure/dashboard')

@app.route('/secure/logout')
def secure_logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/secure/index')

@app.route('/profile')
def profile():
    if request.cookies.get('logged_in') != None:
        user = User.query.filter_by(id=request.cookies.get('user_id')).first()
        print(user)
        return render_template('profile.html', user=user)
    else:
        return redirect('/index')

@app.route('/secure/profile')
def secure_profile():
    if current_user.is_authenticated:
        return render_template('secure_profile.html')
    else:
        return redirect('/index')


@app.route('/secure/search', methods=['get', 'post'])
def secure_search():
    if current_user.is_authenticated:
        form = SearchForm()

        if form.validate_on_submit():
            username = form.username.data
            usernames = []
            users = User.query.filter_by(username=username)
            for user in users:
                usernames.append(user.username)

            return render_template('secure_search.html', form=form, results=usernames)
        else:
            return render_template('secure_search.html', form=form)
    else:
        return redirect('/login')