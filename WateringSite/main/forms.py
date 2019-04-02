from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from WateringSite.models import User, Device
from flask_login import current_user


# Registering brand new (unowned) devices
class NewDeviceForm(FlaskForm):
    new_device_id = IntegerField('Device ID:', validators=[DataRequired()])
    msg = "Device passkey must be 4 to 6 characters."
    device_key = StringField('Device key:', validators=[DataRequired(), Length(min=4, max=6, message=msg)])
    device_key2 = StringField('Device key (repeat):', validators=[DataRequired(), EqualTo('device_key')])
    msg2 = "Device must have a name."
    device_name = StringField('Device name:', validators=[DataRequired(), Length(min=1, max=-1, message=msg2)])
    submit = SubmitField('Register unowned device')

    def validate_new_device_id(self, new_device_id):
        dev = Device.query.filter_by(id=new_device_id.data).first()
        if dev is not None:
            raise ValidationError('Device already exists in system.')


# For profile page. Update your email or add a new device.
class UpdateEmailForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    email2 = StringField('Repeat new email', validators=[Email(), EqualTo('email', message="Email fields do not match.")])
    updateEmailSubmit = SubmitField('Update Email')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


# Adding and removing active devices from accounts
class AddDeviceForm(FlaskForm):
    device_id = IntegerField('Add existing device by id:', validators=[DataRequired()])
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
        if device is None:
            raise ValidationError('Device not found.')
        if device_key.data != device.key:
            raise ValidationError('Invalid device key.')


class RemoveDeviceForm(FlaskForm):
    delete = BooleanField('Remove device from account', validators=[DataRequired()])
    removeDeviceSubmit = SubmitField('Confirm Removal')


class EditDeviceKeyForm(FlaskForm):
    msg = "Secret passkey must be 4 to 6 characters."
    device_key = StringField('Edit device passkey:', validators=[DataRequired(), Length(min=4, max=6, message=msg)])
    device_key2 = StringField('(repeat):', validators=[DataRequired(), EqualTo('device_key', message="Both fields must match.")])
    EditKeySubmit = SubmitField('Submit')


class EditDeviceNameForm(FlaskForm):
    device_name = StringField('Edit device nickname:', validators=[DataRequired()])
    EditNameSubmit = SubmitField('Submit')


