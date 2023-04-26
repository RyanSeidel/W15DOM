# forms.py

# Code description: contains the forms for signup, login form, and search form. The signup form checks if the user already exists in the database and if not, it creates a new user. It also checks if the email or username already exists in the database. If it does, it will flash an error message and redirect the user to the signup page. If the user is successfully created, it will redirect the user to the home page.

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError, InputRequired

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    name = StringField('Username', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Submit')
    search_filter = SelectField('Filter', choices=[('name', 'Name'), ('genre', 'Genre'), ('console', 'Console')])


