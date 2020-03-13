from app import app, hashing, db
from flask import make_response, redirect, render_template
from app.forms import  RegistrationForm, LoginForm
from app.models import User
import secrets

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
    test = hash_password(raw, salt)
    return test == hash

def create_salt():
    return secrets.token_bytes(8)

@app.route('/')
@app.route('/index')
def index():
    return 'Hello world!'

@app.route('/register', methods=['get', 'post'])
def register():
    form = RegistrationForm()
    errors = []

    if form.validate_on_submit():
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        passwords_valid, errors = are_passwords_valid(password1, password2, errors)
        username_valid, errors = is_username_valid(username, errors)

        if username_valid and passwords_valid:
            salt = create_salt()
            password_hash = hash_password(password1, salt=salt)
            new_user = User(username=username, password_hash=password_hash, salt=salt)
            db.session.add(new_user)
            db.session.commit()
            redirect('/login')
    return render_template('register.html', form=form, errors=errors)

@app.route('/login', methods=['get', 'post'])
def login():
    form = LoginForm()
    username = form.username.data
    password = form.password.data
    remember_me = form.remember_me.data

    if form.validate_on_submit():
        if user_exists(username):
            user = User.query.filter_by(username=username).first()
            if hash_password(password, user.salt) == user.password_hash:


    return render_template('login.html', form=form)
