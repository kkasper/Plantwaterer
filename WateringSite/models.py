from WateringSite import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from WateringSite import login
from time import time
import jwt
from WateringSite import app

# Creating the user table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    admin = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(128))
    watering_events = db.relationship('WateringEvent', backref='author', lazy='dynamic')
    devices = db.relationship('Device', secondary='user_device', back_populates="users")

    def __repr__(self):
        return '<User {} {} [{}]>'.format(self.id, self.username, self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_by_id(self, get_id):
        return User.query.filter_by(id=get_id).first()

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class WateringEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    watering_length = db.Column(db.Integer, default=8)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    completed = db.Column(db.Boolean, default=False)
    scheduled_device = db.Column(db.Integer)

    def __repr__(self):
        return '<WateringEvent {0}: {1} seconds at {2}>'.format(self.id, self.watering_length, self.timestamp)


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    owner = db.Column(db.Integer)
    device_name = db.Column(db.String(64), index=True)
    key = db.Column(db.Integer)
    users = db.relationship('User', secondary='user_device', back_populates='devices')

    def __repr__(self):
        return '<Device \"{}\": {}. Key: {}. Owner: {}>'.format(self.device_name, self.id, self.key, self.owner)

    def get_device(self, get_id):
        return Device.query.filter_by(id=get_id).first()


# Creating the association model between users, devices, and users who are owners
class UserDevice(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey(Device.id), primary_key=True)

    def __repr__(self):
        return 'User {} has access to device {}.'.format(self.user_id, self.device_id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
