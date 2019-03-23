from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from WateringSite.models import User


# The fields for form pages. Handles variables/validation
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


# Handles registration of new users. Add new user to a certain device.
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Note that we should be case insensitive when checking for username validity.
    # We filter a query for users by lowercase username == lowercase input. Same for email.
    def validate_username(self, username):
        user = User.query.with_entities(User.username). \
            filter(User.username.ilike(username.data)).first()
        if user is not None:
            raise ValidationError('This username is taken.')

    def validate_email(self, email):
        email_address = User.query.with_entities(User.email). \
            filter(User.email.ilike(email.data)).first()
        if email_address is not None:
            raise ValidationError('Please use a different email.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')