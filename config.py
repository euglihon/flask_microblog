import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMy_TRACK_MODIFICATIONS = False

	# количество постов на странице
	POSTS_PER_PAGE = 3

	# конфигурация емаил сервера
	# локальный эмуляытор mail сервер
	'''(venv) $ python -m smtpd -n -c DebuggingServer localhost:8025
	(venv) $ export MAIL_SERVER=localhost
	(venv) $ export MAIL_PORT=8025'''
	# внешний mail сервер
	'''(venv) $ export MAIL_SERVER=smtp.googlemail.com
	(venv) $ export MAIL_PORT=587
	(venv) $ export MAIL_USE_TLS=1
	(venv) $ export MAIL_USERNAME=<your-gmail-username>
	(venv) $ export MAIL_PASSWORD=<your-gmail-password>'''
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['admin@domain.com']
