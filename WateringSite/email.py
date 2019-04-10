from flask_mail import Message
from flask import current_app, render_template
from WateringSite import mail
from threading import Thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()


def send_guest_access_email(device, sender, recipient):
    token = device.get_guest_access_token((72*60*60))
    send_email('Invitation to a [Plant Party]',
               sender=("{} at HannahsPlants.party".format(sender.username), current_app.config['ADMINS'][0]),
               recipients=[recipient["Email"]],
               text_body=render_template('email/guest_access.txt',
                                         sender=sender, recipient=recipient, token=token),
               html_body=render_template('email/guest_access.html',
                                         sender=sender, recipient=recipient, token=token))

