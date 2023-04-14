from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    search = StringField('Search')
    submit = SubmitField('Submit')
    search_filter = SelectField('Filter', choices=[('name', 'Name'), ('genre', 'Genre'), ('console', 'Console')])

class AddGameForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    image_url = StringField('Image URL', validators=[Optional(), URL()])
    console = SelectField('Console', choices=[('pc', 'PC'), ('ps4', 'PlayStation 4'), ('xbox', 'Xbox One')])
    is_steam = SelectField('Is Steam', choices=[(True, 'Yes'), (False, 'No')])
    submit = SubmitField('Add Game')

    def validate_name(self, name):
        if len(name.data) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        if len(name.data) > 100:
            raise ValidationError('Name cannot be longer than 100 characters.')

