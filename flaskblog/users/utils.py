from PIL import Image
import os
import secrets
from flask_mail import Message
from flaskblog import mail
from flask import url_for, current_app


def save_picture(username, form_pic):
    random_hex = secrets.token_hex(8)
    _, fn_ext = os.path.split(form_pic.filename)
    pic_name = username + '-' + random_hex + fn_ext
    pic_abs_path = os.path.join(current_app.root_path, f'static/profile_pics/{pic_name}')
    output_size = (125, 125)
    img = Image.open(form_pic)
    img.thumbnail(output_size)
    img.save(pic_abs_path)

    return pic_name


def reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="demoappray@gmail.com",
                  recipients=[f"{user.email}"])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)