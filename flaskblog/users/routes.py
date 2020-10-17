from flask import render_template, redirect, flash, request, Blueprint
from flaskblog import bcrypt, db
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordForm, ReqRestForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog.users.utils import *

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_url = request.args.get('next')
            # print(next_url) --> /account
            return redirect(next_url) if next_url else redirect(url_for('main.home'))
        else:
            flash(f"Login unsuccessful. Please check your username and password", 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            pic_name = save_picture(current_user.username, form.picture.data)
            current_user.image_file = pic_name
        db.session.commit()
        flash('Your account details has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@users.route('/user/post/<string:username>', methods=['GET', 'POST'])
def user_post(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)

    return render_template('user_posts.html', user=user, posts=posts, title=f"{username}'s Posts")


@users.route('/reset_password', methods=['GET', 'POST'])
def req_reset():
    form = ReqRestForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        reset_email(user)
        flash('An email has been sent with further instructions', 'info')
        return redirect(url_for('users.login'))
    return render_template('req_reset.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    form = ResetPasswordForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('users.req_reset'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been updated!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
