from WateringSite import app, db
from flask import render_template, flash, redirect, url_for, request
from WateringSite.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from WateringSite.models import User
from werkzeug.urls import url_parse
from WateringSite.forms import ResetPasswordRequestForm, ResetPasswordForm
from WateringSite.email import send_password_reset_email


@app.route('/')
@app.route('/home')
def home():
    wateringevents = [
        {
            'author': {'username': 'John'},
        },
        {
            'author': {'username': 'Susan'},
        }
    ]
    return render_template('index.html', title='Home', wateringevents=wateringevents)


# Allows for POST as well as GET. Checks for valid login and hashed passwords. Checks if URL has next page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Register a new user account
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have registered a new user account!')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


# For adding and removing control of devices to account
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form1 = UpdateEmailForm()
    form2 = AddDeviceForm()
    if form1.updateEmailSubmit.data and form1.validate():
            current_user.email = form1.email.data
            db.session.commit()
            flash('Email updated!')
            return redirect(url_for('home'))
    if form2.addDeviceIDSubmit.data and form2.validate():
        dev = Device.query.filter_by(id=form2.device_id.data).first()
        current_user.devices.append(dev)
        db.session.commit()
        flash('Device added to account!')
        return redirect(url_for('profile'))

    return render_template('profile.html', title='User Profile', form1=form1, form2=form2,
                           devices=current_user.devices, User=current_user)


# For registering a brand new device to the system
@app.route('/new_device', methods=['GET', 'POST'])
@login_required
def new_device():
    form = NewDeviceForm()
    if form.validate_on_submit():
        device = Device(id=form.new_device_id.data, key=form.device_key.data,  device_name=form.device_name.data,
                        owner=current_user.id)
        db.session.add(device)
        current_user.devices.append(device)
        db.session.commit()
        flash('You have registered a new device!')
        return redirect(url_for('home'))
    return render_template('new_device.html', title='Register new device', form=form)


# For editing an existing device
@app.route('/edit_device/<device_id>', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    if device not in current_user.devices:
        return redirect(url_for('home'))
    form1 = EditDeviceKeyForm()
    form2 = EditDeviceNameForm()
    form3 = RemoveDeviceForm()
    if form1.EditKeySubmit.data and form1.validate():
        device.key = form1.device_key.data
        db.session.commit()
        flash('Passkey updated.')
        return redirect(url_for('edit_device', device_id=device.id))
    if form2.EditNameSubmit.data and form2.validate():
        device.device_name = form2.device_name.data
        db.session.commit()
        flash('Device name updated.')
        return redirect(url_for('edit_device', device_id=device.id))
    if form3.removeDeviceSubmit.data and form3.validate():
        current_user.devices.remove(device)
        db.session.commit()
        flash('Device removed from account!')
        return redirect(url_for('profile'))
    return render_template('edit_device.html', title='Edit Device Settings', form1=form1, form2=form2, form3=form3,
                           device=device)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('home'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
