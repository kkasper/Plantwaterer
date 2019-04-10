import os
from collections import defaultdict
from datetime import datetime
from WateringSite import db
from flask import render_template, flash, redirect, url_for, send_from_directory, current_app, request, jsonify
from flask_login import login_required
from WateringSite.email import send_guest_access_email
from WateringSite.main.forms import *
from WateringSite.models import Device, WateringEvent, User
from WateringSite.contributionchart import render_html
from WateringSite.main import bp
from WateringSite.auth.email import send_admin_password_reset_email


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static/favicon'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        if request.form.get('delete_button') == 'event':
            event_id = request.form['event_id']
            wevent = WateringEvent.query.filter_by(id=event_id).first_or_404()
            db.session.delete(wevent)
            db.session.commit()
            flash("Scheduled watering has been removed!")
            return redirect(url_for('main.home'))
        if request.form.get('submit_button') == 'Schedule' and request.form.get('scheduled_date'):
            date_time = datetime.fromtimestamp(int(request.form['scheduled_date']))
            device_id = request.form['device_id']
            wevent = WateringEvent(timestamp=date_time, author_id=current_user.id, device_id=device_id)
            db.session.add(wevent)
            db.session.commit()
            return redirect(url_for('main.home'))
        elif request.form.get('submit_button') == 'Water Now':
            device_id = request.form['device_id']
            date_time = datetime.now()
            wevent = WateringEvent(timestamp=date_time, author_id=current_user.id, device_id=device_id)
            db.session.add(wevent)
            db.session.commit()
            return redirect(url_for('main.home'))
        else:
            pass

    devices = current_user.devices
    eventsdict = defaultdict(lambda: defaultdict(list))
    for d in range(len(devices)):
        for e in devices[d].watering_events.all():
            eventsdict[d][e.get_parser_date()].append(e.get_ftime())

    return render_html.create_graph(devices, eventsdict)


# For adding and removing control of devices to account
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form1 = UpdateEmailForm()
    form2 = GuestAccessForm()
    if form1.validate_on_submit():
        current_user.email = form1.email.data
        db.session.commit()
        flash("Email updated.")
        return redirect(url_for('main.profile'))
    if form2.validate_on_submit():
        device = Device.query.get(form2.device_id.data)
        recipient = {"Name": form2.casual_name.data, "Email": form2.recipient_email.data}
        send_guest_access_email(device, current_user, recipient)
        flash('An invitation to access your device has been sent to {}.'.format(form2.recipient_email.data))
        return redirect(url_for('main.profile'))
    if request.form.get('guest_access_id'):
        device = Device.query.get(request.form['guest_access_id'])
        device.guests_allowed = not device.guests_allowed
        db.session.commit()
        flash('Guest privileges have been updated.')
        return redirect(url_for('main.profile'))
    if request.form.get('displaystatus_device_id'):
        device = Device.query.get(request.form['displaystatus_device_id'])
        device.display_open = not device.display_open
        db.session.commit()
        flash('Display preference updated.')
        return redirect(url_for('main.profile'))

    return render_template('profile.html', title='User Profile', form1=form1, form2=form2,
                           devices=current_user.devices, User=current_user)


# For registering a brand new device to the system
@bp.route('/new_device', methods=['GET', 'POST'])
@login_required
def new_device():
    form = NewDeviceForm()
    if form.validate_on_submit():
        device = Device.query.filter_by(id=form.new_device_serial.data).first()
        device.owner = current_user.id
        current_user.devices.append(device)
        db.session.commit()
        flash('You have registered a device to your account!')
        return redirect(url_for('main.home'))
    return render_template('new_device.html', title='Register new device', form=form)


# For editing an existing device
@bp.route('/edit_device/<device_id>', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    device = Device.query.filter_by(id=device_id).first_or_404()
    if device not in current_user.devices:
        return redirect(url_for('main.home'))
    form1 = EditDeviceNameForm()
    form2 = RemoveDeviceForm()
    if form1.EditNameSubmit.data and form1.validate():
        if device.owner is not current_user.id:
            flash('Only the owner of the device can change the name.')
            return redirect(url_for('main.edit_device', device_id=device.id))
        device.name = form1.device_name.data
        db.session.commit()
        flash('Device name updated.')
        return redirect(url_for('main.edit_device', device_id=device.id))
    if form2.removeDeviceSubmit.data and form2.validate():
        current_user.devices.remove(device)
        device.owner = 0
        db.session.commit()
        flash('Device removed from account!')
        return redirect(url_for('main.profile'))
    return render_template('edit_device.html', title='Edit Device Settings', form1=form1, form2=form2,
                           device=device)


# TODO: Admin panel with tables for users, devices, watering events
@bp.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    devices = Device.query.all()
    users = User.query.all()
    events = WateringEvent.query.all()
    if request.method == 'POST':
        if request.form.get('user_id_to_reset'):
            user_id = request.form['user_id_to_reset']
            user = User.query.filter_by(id=user_id).first_or_404()
            send_admin_password_reset_email(user)
            flash('Password reset email sent to {} at {}.'.format(user.username, user.email))
            return redirect(url_for('main.admin_panel'))
        if request.form.get('admin_status_user_id'):
            user = User.query.get(request.form['admin_status_user_id'])
            user.admin = not user.admin
            db.session.commit()
            flash('Admin status updated.')
            return redirect(url_for('main.admin_panel'))
        if request.form.get('delete_button') == 'device':
            device_id = request.form['device_id']
            device = Device.query.filter_by(id=device_id).first_or_404()
            for event in device.watering_events:
                db.session.delete(event)
            db.session.delete(device)
            db.session.commit()
            flash('Device deleted!')
            return redirect(url_for('main.admin_panel'))
        elif request.form.get('delete_button') == 'user':
            user_id = request.form['user_id']
            user = User.query.filter_by(id=user_id).first_or_404()
            for event in user.watering_events:
                db.session.delete(event)
            db.session.delete(user)
            db.session.commit()
            flash('User account deleted!')
        elif request.form.get('delete_button') == 'event':
            event_id = request.form['event_id']
            event = WateringEvent.query.filter_by(id=event_id).first_or_404()
            db.session.delete(event)
            db.session.commit()
            flash('Watering event deleted!')
            return redirect(url_for('main.admin_panel'))
        elif request.form.get('create_device'):
            device = Device()
            db.session.add(device)
            db.session.commit()
            flash('New device generated!')
            return redirect(url_for('main.admin_panel'))
        else:
            pass

    return render_template('admin_page.html', title='Admin Panel', devices=devices, users=users, events=events, User=current_user)


@bp.route('/credits')
def site_credits():
    return render_template('credits.html', title='Credits')


@bp.route('/grant_access/<token>', methods=['GET', 'POST'])
@login_required
def grant_access(token):
    device = Device.verify_guest_access_token(token)
    if not device:
        return redirect(url_for('main.home'))

    if device in current_user.devices:
        flash('You already had access to this device.')
        return redirect(url_for('main.home'))

    current_user.devices.append(device)
    db.session.commit()
    flash('You now have access to {}.'.format(device.device_name))
    return redirect(url_for('main.home'))
