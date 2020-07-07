from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import LoginManager

from flask_mail import Mail

from flask_bootstrap import Bootstrap

from flask_moment import Moment # расширение для конвертация времени юзера в utc




app = Flask(__name__)
app.config.from_object(Config)


bootstrap = Bootstrap(app)


moment = Moment(app) # +++ необходимо добавить а базовый шаблон
# {% block scripts %}
#     {{ super() }}
#     {{ moment.include_moment() }}
# {% endblock %}


mail = Mail(app)


login = LoginManager(app)
login.login_view = 'login' # автоматическое перенаправление на функцию login (если пользователь не зарегистрирован)


db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routers, models, errors


