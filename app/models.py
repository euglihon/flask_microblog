from hashlib import md5  # либа для работы с сервисом gravatar

from app import db
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin



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

    def __repr__(self):
        return f'<User {self.username}>'




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post {self.body}>'
