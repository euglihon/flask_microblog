from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm

from app import login
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User

from app import db

from datetime import datetime


@login.user_loader # автоматически регистрирует загрзк. пользователя (отслеживание)
#  функция для работы flask-login (current_user и тд)
def load_user(id):
    return User.query.get(int(id))


@app.before_request # функция автоматически будет выполнена перед функциями отрисовки для записи времени
def before_request():
    if current_user.is_authenticated:
        # если юзер залогирован
        # запись залогининому юзеру в поле last_seen времени
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


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


# страница профиля
@app.route('/user/<username>')  # динамическое приписание  username
@login_required  # защита от анонимного входа
def user(username):
    # поиск юзера с входным именем в таблице
    # first_or_404() -- работает как first()б но если результата нет вернет 404
    user = User.query.filter_by(username=username).first_or_404()

    # временный список
    posts = [
        {'author': user.username, 'body': 'Test post #1'},
        {'author': user.username, 'body': 'Test post #2'},
    ]

    return render_template('user.html', posts=posts, user=user)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required  # защита от анонимного входа
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        # если форма отправлена
        # записываем новые значения залог. юзеру в таблице User из получе. данных из формы
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        # флешем отправляем сообшение в базовый шаблон
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))

    elif request.method == 'GET': # пустая загрузка формы (до отправки формы)
        # записываем в поля формы информацию из таблици
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)