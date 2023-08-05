from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, EqualTo, Length
from email_validator import validate_email

class RegisterForm(FlaskForm):
    username = StringField("Enter a Username", validators=[InputRequired()])
    password = PasswordField("Enter a Password", validators=[InputRequired(),
                            EqualTo('confirm', message="Passwords must match.")])
    confirm = PasswordField("Re-enter Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Enter your Username", validators=[InputRequired()])
    password = PasswordField("Enter your Password", validators=[InputRequired()])

class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(max=30)])
    content = TextAreaField('Content', validators=[InputRequired()])