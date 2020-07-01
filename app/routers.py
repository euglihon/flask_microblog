from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from app import app
from app.forms import LoginForm, RegistrationForm

from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

from app import db


@app.route('/')
@app.route('/index')
@login_required  # декоратор(flask-login) зашишает от анонимного юзера функцию и перенаправляет на '/login'
# + декоратор передаст GET значение   Next   в функцию login, чтобы после логирования вернуться на нужную страницу
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        },
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }]
    return render_template('index.html', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # зарегистрирован ли пользователь
        # если так то редирект
        return redirect(url_for('index'))

    # создаем форму логирования из models.forms
    form = LoginForm()

    if form.validate_on_submit():
        # если форма отправленна
        # находим юзера в таблице по данным введенным в форму
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or user.check_password(form.password.data) == False:
            # eсли юзер не создался ИЛИ метод проверки пароля (из класса User)  вернуда False
            # (передаем поле пароль из формы)
            # flash перелаем сообщение в index.html
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            # Если все ок передаем в метод flask-login пользователя
            # + проверяем нунжо ли его запомнить (из поля формы)
            login_user(user, remember=form.remember_me.data)

            # !!!!!! принимаем значения некст
            #(зашишенная страница на которую не удалось попасть анонимному юзеру) из декоратора @login_required !!!!!
            nex_page = request.args.get('next')
            if not nex_page or url_parse(nex_page).netloc != '':
                # если нет значения Next в декораторе @login_required то перенаправим просто в index
                nex_page = url_for('index')

            return redirect(nex_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    # метод из flask-login
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # flask-login проверка залогирован ли пользователь
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Если форма отправленна
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)