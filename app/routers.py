from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from app import app
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm

from app import login
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post

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




@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required  # декоратор(flask-login) зашишает от анонимного юзера функцию и перенаправляет на '/login'
# + декоратор передаст GET значение   Next   в функцию login, чтобы после логирования вернуться на нужную страницу
def index():
    form = PostForm()
    # Создание поста на главной странице
    if form.validate_on_submit():
        # Если форма отправлн.
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('You post is now live!')
        return redirect(url_for('index'))

    # записываем результат функции поиска всех постов на которые подписан и своих (models User)
    posts = current_user.followed_posts()

    # Создание пагинации (номер страницы)
    page = request.args.get('page', 1, type=int)
                                # количество постов возьмет из конфина
                                                             # обработка вне диапзона
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    # Созадние линков для перелистывания страниц пагинации
    # из стандартных элементов paginate
    # если страница (has_next, has_prev) в конце то ссылка будет None
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
                                                    # items нужно для работы пагинации
    return render_template('index.html', posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)




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
    posts = user.posts.all()
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




# подписаться на юзернайма
@app.route('/follow/<username>')
@login_required
def follow(username):
    # запис. в переменную нужного юзера
    user = User.query.filter_by(username=username).first()
    if user is None:
        # Если такой юзер не нашелся
        flash(f'USer {username} not found')
        return redirect(url_for('index'))

    if user == current_user:
        # Если юзер == залогиненый юзер
        flash('You cannot follow yourself!')
        # Редирект на страницу своего профиля
        return redirect(url_for('user', username=username))

    # Если все ок выполняем функцию фолоу у залог юзера (передаем в функцию юзера, которого нашли)
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}')
    # Редикерт на страницу этого юзера
    return redirect(url_for('user', username=username))




@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(f'USer {username} not found')
        return redirect(url_for('index'))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}')
    return redirect(url_for('user', username=username))




# Страница глобального потока всех сообщений
@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc())

    # настройка пагинации постов
    page = request.args.get('page', 1, type=int)
    posts = posts.paginate(page, app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)
