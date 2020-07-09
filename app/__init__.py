from flask import Flask, request
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment # либа для перевода времени пользователя в utc
from flask_babel import Babel # либа для транслитерации текста


app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

moment = Moment(app) # +++ необходимо добавить а базовый шаблон вызов скрипта

mail = Mail(app)

babel = Babel(app)

login = LoginManager(app)
login.login_view = 'login' # автоматическое перенаправл. на функцию login (если пользователь не зарегистрирован)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


@babel.localeselector
def get_locale():
    # выбор языка для каждого запроса для выбора перевода
    return request.accept_languages.best_match(app.config['LANGUAGES'])
    #return 'ru'

from app import routers, models, errors


