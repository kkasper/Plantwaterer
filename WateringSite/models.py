from WateringSite import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from WateringSite import login


# Creating the user table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    watering_events = db.relationship('WateringEvent', backref='author', lazy='dynamic')
    devices = db.relationship('Device', secondary='user_device', backref="users")

    def __repr__(self):
        return '<User {} {} [{}]>'.format(self.id, self.username, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WateringEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    watering_length = db.Column(db.Integer, default=8)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    scheduled_device = db.Column(db.Integer)

    def __repr__(self):
        return '<WateringEvent {0}: {1} seconds at {2}>'.format(self.id, self.watering_length, self.timestamp)


# TODO: Finish device model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    device_name = db.Column(db.String(64))
    key = db.Column(db.Integer)

    def __repr__(self):
        return '<Device \"{}\": {}. Key: {}. Owner: {}>'.format(self.device_name, self.id, self.key, self.owner)

    def set_owner(self, owner_id):
        self.owner = owner_id

# Creating the association model between users, devices, and users who are owners
class UserDevice(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(Device.id), primary_key=True)
    owner = db.Column(db.Boolean, default=(Device.owner == User.id))
    user = db.relationship('User', backref=db.backref('user_device', passive_deletes='all'))
    device = db.relationship('Device', backref=db.backref('user_device', passive_deletes='all'))

    def __repr__(self):
        return 'User {} has access to device {}. Owner: {}'.format(self.user_id, self.device_id, self.owner)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
