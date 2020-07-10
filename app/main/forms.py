from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_babel import _, lazy_gettext as _1

# Форма создания поста на главной
class PostForm(FlaskForm):
    post = TextAreaField(_1('Say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_1('Submit'))


class EditProfileForm(FlaskForm):
    username = StringField(_1('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_1('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_1('Submit'))

