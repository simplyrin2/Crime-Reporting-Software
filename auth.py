from config import config
from __init_app__ import app
from models import User, db

from flask_login import LoginManager
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from flask_bcrypt import Bcrypt

app.config['SECRET_KEY'] = config['SECRET_KEY']
bycrpyt = Bcrypt(app) # Hashing passwords

login_manager = LoginManager()

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20), EqualTo(fieldname='confirm_password', message='Passwords must match')], render_kw={})
    confirm_password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])

    submit = SubmitField("Register")
    
    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Username already exists")
    
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={})

    submit = SubmitField("Login")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        print(existing_user_username)
        if existing_user_username is None:
            raise ValidationError('Username not found')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            if bycrpyt.check_password_hash(user.password, password.data):
                pass
            else:
                raise ValidationError('Incorrect password')
    