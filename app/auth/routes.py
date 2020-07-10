from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, \
    ResetPasswordRequestForm
from app.auth.email import sent_password_reset_email

from flask_babel import _

from app import db
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # зарегистрирован ли пользователь
        # если так то редирект
        return redirect(url_for('main.index'))
    # создаём форму логирования
    form = LoginForm()

    if form.validate_on_submit():
        # если форма выслана
        # находим юзера в таблице по данным из форму
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or user.check_password(form.password.data) == False:
            # eсли юзер не создался ИЛИ метод проверки пароля (из класса User) вернул False
            # flash -- передаём сообщение в index.html
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        else:
            # Если все ок передаём в метод flask-login пользователя
            # + проверяем нужно ли его запомнить (из поля формы)
            login_user(user, remember=form.remember_me.data)

            # !!!!!! принимаем значение next
            # (next - страница на которую не удалось попасть анонимному юзеру) из декоратора @login_required !!!!!
            nex_page = request.args.get('next')
            if not nex_page or url_parse(nex_page).netloc != '':
                # если нет значения Next в декораторе @login_required то редирект просто наЫ index
                nex_page = url_for('main.index')

            return redirect(nex_page)
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    # метод из flask-login
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # flask-login проверка вошел ли пользователь
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Если форма выслана
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            sent_password_reset_email(user)
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/password_reset.html', title=_('Reset password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
