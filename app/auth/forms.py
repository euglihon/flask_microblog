from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from app.models import User
from flask_babel import _, lazy_gettext as _1


class LoginForm(FlaskForm):
    username = StringField(_1('Username'), validators=[DataRequired()])
    password = PasswordField(_1('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_1('Remember me'))
    submit = SubmitField(_1('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_1('Username'), validators=[DataRequired()])
    email = StringField(_1('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_1('Password'), validators=[DataRequired()])
    # EqualTo - валидация второй строки пароля с первой
    password2 = PasswordField(_1('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_1('Register'))

    def validate_username(self, username):
        # поиск юзера из строки формы username в таблице User
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            # Если такой юзер есть,  то выдаем встроенную ошибку в wtforms
            raise ValidationError(_1('Please use a different username'))

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError(_1('Please use a different email address'))


# форма для сброса пароля
class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_1('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_1('Password reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_1('Password'), validators=[DataRequired()])
    password2 = PasswordField(_1('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_1('Request Password Reset'))
