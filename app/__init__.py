from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment # либа для перевода времени пользователя в utc
from flask_babel import Babel, _ # либа для транслитерации текста


db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
login.login_view = 'auth.login' # автоматическое перенаправл. на функцию login (если пользователь не зарегистрирован)
login.login_message = _('Please log in to app')

babel = Babel()

moment = Moment() # +++ необходимо добавить а базовый шаблон вызов скрипта

bootstrap = Bootstrap()

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    login.init_app(app)
    mail.init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # регистрация блюпринтов
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app


@babel.localeselector
def get_locale():
    # выбор языка для каждого запроса для выбора перевода
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
    #return 'ru'


from app import models









