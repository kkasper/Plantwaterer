from WateringSite import app, db
from flask import render_template, flash, redirect, url_for, request
from WateringSite.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from WateringSite.models import User
from werkzeug.urls import url_parse


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


# TODO: Add profile HTML and finish form handling
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form1 = UpdateEmailForm()
    form2 = AddDeviceForm()
    form3 = RemoveDeviceForm()
    if form1.updateEmailSubmit.data and form1.validate():
            current_user.email = form1.email
            db.session.commit()
            flash('Email updated!')
            return redirect(url_for('home'))
    if form2.addDeviceIDSubmit.data and form2.validate():
        print("test")
    if form3.removeDeviceSubmit.data and form3.validate():
        # TODO: Enumerate devices owned / guest devices
        print("test2")

    return render_template('profile.html', title='User Profile', form1=form1, form2=form2, form3=form3)


# TODO: Managing device serial and passkeys
@app.route('/new_device', methods=['GET', 'POST'])
@login_required
def new_device():
    form = NewDeviceForm()
    if form.validate_on_submit():
        device = Device.query.filter_by(id=form.device_id.data).first()
        device.owner = current_user

        db.session.commit()
        flash('You have registered a new device!')
        return redirect(url_for('home'))
    return render_template('new_device.html', title='Register new device', form=form)