from flask_mail import Message
from flask import render_template, current_app
from app import mail
from threading import Thread
from flask_babel import _


def send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def sent_email(subject, sender, recipients, text_body, html_body):
    message = Message(subject, sender=sender, recipients=recipients)
    message.body = text_body
    message.html = html_body
    Thread(target=send_async_email, args=(current_app.get_current_object(), message)).start()


def sent_password_reset_email(user):
    token = user.get_reset_password_token()
    sent_email(_('Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('auth/email/reset_password.html',
                                         user=user, token=token))