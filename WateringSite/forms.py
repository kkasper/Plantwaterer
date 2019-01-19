from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from WateringSite.models import User, Device


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

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Registering brand new (unowned) devices
class NewDeviceForm(FlaskForm):
    device_id = StringField('Device ID', validators=[DataRequired()])
    device_key = StringField('Device Passkey', validators=[DataRequired()])
    submit = SubmitField('Register unowned device')

    def validate_devicekey(self, device_id, device_key):
        device = Device.query.filter_by(id=device_id.data).first()
        if device is not None:
            raise ValidationError('Device already exists in system.')


# For profile page. Update your email or add a new device.
class UpdateEmailForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    email2 = StringField('Repeat new email', validators=[Email(), EqualTo('email')])
    updateEmailSubmit = SubmitField('Update Email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Adding and removing active devices from accounts
class AddDeviceForm(FlaskForm):
    deviceID = StringField('Device ID:')
    deviceKey = StringField('Device key:')
    addDeviceIDSubmit = SubmitField('Add new Device')


class RemoveDeviceForm(FlaskForm):
    deviceID = StringField('Device ID:')
    removeDeviceSubmit = SubmitField('Remove Device from Account')
