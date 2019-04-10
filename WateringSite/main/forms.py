from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from WateringSite.models import User, Device
from flask_login import current_user


# Registering brand new (unowned) devices
class NewDeviceForm(FlaskForm):
    new_device_serial = IntegerField('Device Serial Number:', validators=[DataRequired()])
    device_uid = StringField('Device unique ID:', validators=[DataRequired()])
    device_uid2 = StringField('Device unique ID (repeat):', validators=[DataRequired(), EqualTo('device_uid')])
    submit = SubmitField('Register unowned device')

    def validate_new_device_serial(self, new_device_serial):
        device = Device.query.filter_by(id=new_device_serial.data).first()
        if device.owner is not 0:
            raise ValidationError('Device is already owned by someone.')

    def validate_device_uid(self, device_uid):
        device = Device.query.filter_by(id=self.new_device_serial.data).first()
        if not device_uid.data == device.key:
            raise ValidationError('Device information is not valid.')


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


class EditDeviceNameForm(FlaskForm):
    device_name = StringField('Edit device nickname:', validators=[DataRequired()])
    EditNameSubmit = SubmitField('Submit')


class GuestAccessForm(FlaskForm):
    casual_name = StringField('Recipient name (optional):')
    recipient_email = StringField('Recipient email', validators=[Email()])
    recipient_email2 = StringField('Repeat email', validators=[Email(), EqualTo('recipient_email', message="Email fields do not match.")])
    device_id = IntegerField("Device Serial Number:")
    guestInviteSubmit = SubmitField('Send invitation')
