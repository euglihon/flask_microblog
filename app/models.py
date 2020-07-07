from hashlib import md5  # либа для работы с сервисом gravatar

import jwt # либа для создания токенов (сброс пароля)
from time import time

from app import app

from app import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin


#Вспомогательная таблица для связи many-to-many User--User
followers = db.Table('followers',
                        db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),# кто подписан
                        db.Column('followed_id', db.Integer, db.ForeignKey('user.id')) # на кого подписан
                   )


class User(UserMixin, db.Model): # add Mixin(flask-login)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    # поле сетается из функции set_password
    password_hash = db.Column(db.String(128))
    # статус юзера
    about_me = db.Column(db.String(140))
    # данные о последнем логировании пользователя
    last_seen = db.Column(db.DateTime)

    # указатель на создание связи с таблицей Post и для обратной связи через таблицу User
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    #связь многие со многими (в массиве будет храниться на кого подписан пользователь)
    followed = db.relationship(
                    # 'User' - таблица с которой делаем связь, secondary-- назавние доп. таблицы связи
                    'User', secondary=followers,
                    primaryjoin=(followers.c.follower_id == id),
                    secondaryjoin=(followers.c.followed_id == id),
                    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
            )

    def follow(self, user):
        if not self.is_following(user):
            # если пользователь не подписан на юзера то добавляем его в массив (на кого подписан пользоаватель)
            self.followed.append(user)

    def unfollow(self, user):
        # если подписан на юзера то удаляем его из массива на кого подписан пользователь
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        # проверка подписаны ли залогированный пользователь на юзера. Если да то 1 если нет то 0
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        # запрос к БД для получения постов на которые подписан залог. пользователь
                        #join временное слияние таблиц
                                            # условие обьединений( на кого подписаны все с их постами,
                                                        # за которыми следят разные пользователи)
                                            # filter выборка тех постов на которые подписан(folower) залог пользователь
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id))\
                                    .filter(followers.c.follower_id == self.id)
        # поиск постов которые принадлежат залог пользователю
        own = Post.query.filter_by(user_id=self.id)
        # совмещаем посты на которые подписан и свои, сортируем по времени
        return followed.union(own).order_by(Post.timestamp.desc())


    def set_password(self, password):
        # метод создания пароля и записи хеша в таблице
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # метод сравнения пароля с значением в хеше (True/False)
        return check_password_hash(self.password_hash, password)


    def get_avatar(self, size):
        # временная логика для генерации аватаров загруженных на gravatar.com
        # grabatar позволяет к каждому email прикрепить фото
                    # берем email из таблицы
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod # статическиц метод
    def verify_reset_password_token(token):
        # проверка токена на подлиноть
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['rest_password']
        except:
            return
        return User.query.get(id)



    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'