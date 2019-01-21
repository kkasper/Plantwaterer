from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from WateringSite.models import User, Device
from flask_login import current_user


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
    new_device_id = IntegerField('Device ID:', validators=[DataRequired()])
    msg = "Device passkey must be 4 to 6 characters."
    device_key = StringField('Device key:', validators=[DataRequired(), Length(min=4, max=6, message=msg)])
    device_key2 = StringField('Device key (repeat):', validators=[DataRequired(), EqualTo('device_key')])
    device_name = StringField('Device name:', validators=[DataRequired()])
    submit = SubmitField('Register unowned device')

    def validate_new_device_id(self, new_device_id):
        dev = Device.query.filter_by(id=new_device_id.data).first()
        if dev is not None:
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
    device_id = IntegerField('Add new device by id:', validators=[DataRequired()])
    device_key = StringField('Device secret passkey:', validators=[DataRequired()])
    addDeviceIDSubmit = SubmitField('Add device')

    def validate_device_id(self, device_id):
        device = Device.query.filter_by(id=device_id.data).first()
        if device is None:
            raise ValidationError('Device does not exist in system.')
        elif device in current_user.devices:
            raise ValidationError('You already have access to this device.')

    def validate_device_key(self, device_key):
        device = Device.query.filter_by(id=self.device_id.data).first()
        if device is not None and device.key != device_key.data:
            raise ValidationError('Invalid device key.')


class RemoveDeviceForm(FlaskForm):
    delete = BooleanField('Click to confirm')
    removeDeviceSubmit = SubmitField('Remove Device from Account')


class EditDeviceKeyForm(FlaskForm):
    msg = "Secret passkey must be 4 to 6 characters."
    device_key = StringField('Device passkey:', validators=[DataRequired(), Length(min=4, max=6, message=msg)])
    device_key2 = StringField('Device passkey (repeat):', validators=[DataRequired(), EqualTo('device_key')])
    EditKeySubmit = SubmitField('Edit passkey')


class EditDeviceNameForm(FlaskForm):
    device_name = StringField('Device nickname:', validators=[DataRequired()])
    EditNameSubmit = SubmitField('Edit nickname')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')