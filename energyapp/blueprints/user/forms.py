from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms_components import EmailField, Email
from wtforms_alchemy import Unique
from flask_login import current_user

from energyapp.blueprints.user.models import User, db
from lib.util_wtforms import ModelForm


class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField('Username or email',
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    # remember = BooleanField('Stay signed in')


class SignupForm(ModelForm):
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])


class UpdateAccountForm(FlaskForm):
    email = EmailField(validators=[
        DataRequired(),
        Email()])

    submit = SubmitField('Update')


    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')
