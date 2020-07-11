from flask import render_template, flash, redirect, url_for, request, g, current_app, jsonify
from app import db

from app.main import bp

from flask_login import current_user, login_required

from app.main.forms import PostForm, EditProfileForm, SearchForm, MessageForm
from app.models import User, Post, Message, Notification

from datetime import datetime
from flask_babel import _, get_locale

# библиотека дял определения языка на клиенте (создание постов)
from guess_language import guess_language


@bp.before_app_request
def before_request():
    # функция автоматически будет выполнена перед функциями рендера для записи времени
    if current_user.is_authenticated:
        # если пользователь залог.
        # запись залог. юзеру в поле last_seen времени
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

        g.search_form = SearchForm()
    g.locale = str(get_locale())  # для определения языка пользователя


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required  # декоратор(flask-login) защита от анонимного и перенаправление на '/login'
# + декоратор передаст GET значение   Next   в функцию login, чтобы после входа вернуться на нужную страницу
def index():
    form = PostForm()
    # Форма создание поста на главной странице
    if form.validate_on_submit():
        # Если форма выслана
        # Определение языка в создаваемого поста
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''

        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('You post is now live!'))
        return redirect(url_for('main.index'))

    # записываем результат функции поиска всех постов на которые подписан и своих (models User)
    posts = current_user.followed_posts()

    # Создание пагинации
    page = request.args.get('page', 1, type=int)
    # количество постов на странице берем из конфина
    posts = posts.paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    # Создание ссылок для перелистыв. страниц с помощью пагинации
    # из стандартных элементов paginate
    # если страница (has_next, has_prev) в конце то ссылка будет None
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    # items нужно для работы пагинации
    return render_template('index.html', posts=posts.items, title=_('Home'), form=form, next_url=next_url,
                           prev_url=prev_url)


# страница профиля
@bp.route('/user/<username>')  # динамическое заполнения из вызова функции username
@login_required  # защита от анонимного входа
def user(username):
    # поиск юзера с входным именем в таблице
    # first_or_404() -- работает как first() но если результата нет вернет 404
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).all()
    return render_template('user.html', posts=posts, user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required  # защита от анонимного входа
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        # если форма отправлена
        # записываем новые значения залог. юзеру в таблице User из получе. данных из формы
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        # флешем отправляем сообщение в базовый шаблон
        flash(_('Your changes have been saved'))
        return redirect(url_for('main.edit_profile'))

    elif request.method == 'GET':  # пустая загрузка формы (до отправки формы)
        # записываем в поля формы информацию из таблицы
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title=_('Edit profile'), form=form)


# подписаться на юзернайма
@bp.route('/follow/<username>')
@login_required
def follow(username):
    # запис. в переменную нужного юзера
    user = User.query.filter_by(username=username).first()
    if user is None:
        # Если такой юзер не нашелся
        flash(_('User %(username)s not found', username=username))
        return redirect(url_for('main.index'))

    if user == current_user:
        # Если юзер == залогиненый юзер
        flash(_('You cannot follow yourself!'))
        # Редирект на страницу своего профиля
        return redirect(url_for('main.user', username=username))

    # Если все ок выполняем функцию фолоу у залог юзера (передаем в функцию юзера, которого нашли)
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s', username=username))
    # Редикерт на страницу этого юзера
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(_('User %(username)s not found', username=username))
        flash(f'USer {username} not found')
        return redirect(url_for('main.index'))

    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s', username=username))
    return redirect(url_for('main.user', username=username))


# Страница глобального потока всех сообщений
@bp.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc())

    # настройка пагинации постов
    page = request.args.get('page', 1, type=int)
    posts = posts.paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title=_('Explore'), posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)


# Отправка личных сообзений
@bp.route('/sent_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        # через обратные ссылки author,recipient из User table
        message = Message(author=current_user, recipient=user, body=form.message.data)
        # функция уведомления
        user.add_notification('unread_message_count', user.new_messages())
        db.session.add(message)
        db.session.commit()
        flash(_('You message has been sent'))
        return redirect(url_for('main.user', username=recipient))

    return render_template('send_message.html', title=_('Send Message'), form=form, recipient=recipient)


# Проверка личных сообщений
@bp.route('/message')
@login_required
def messages():
    # записываем в таблицу актуальное время просмотра сообщений залог. юзера
    current_user.last_message_read_time = datetime.utcnow()
    # чистим счетчик вход. сообщений
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    # поиск входящих собщений
    messages = current_user.messages_received.order_by(Message.timestamp.desc())

    page = request.args.get('page', 1, type=int)
    messages = messages.paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) \
        if messages.has_prev else None

    return render_template('messages.html', messages=messages.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])