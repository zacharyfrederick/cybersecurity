from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired
from wtforms import validators

class LoginForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired()])
    password1=PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    tagline = StringField('Tag Line', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    image = StringField('Image Link')
    submit = SubmitField('Register')

class ChompForm(FlaskForm):
    body = StringField('Chomp', validators=[DataRequired()])
    submit = SubmitField('Send it')

class SearchForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Search')

