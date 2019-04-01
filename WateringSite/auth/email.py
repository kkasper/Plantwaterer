from flask import render_template, current_app
from WateringSite.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Plant Party] Reset your password',
               sender=("Plant Party Admin", current_app.config['ADMINS'][0]),
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_admin_password_reset_email(user):
    token = user.get_reset_password_token((60*60*72))
    send_email('[Plant Party] Your password was reset by an Admin',
               sender=("Plant Party Admin", current_app.config['ADMINS'][0]),
               recipients=[user.email],
               text_body=render_template('email/admin_reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/admin_reset_password.html',
                                         user=user, token=token))
