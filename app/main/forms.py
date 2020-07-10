from flask import request
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


class SearchForm(FlaskForm):
    q = StringField(_1('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)