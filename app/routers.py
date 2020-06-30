from flask import render_template, flash, redirect

from app import app
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
	user = {'username': 'Eugenij'}
	posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }, 
        {
            'author': {'username': 'Ипполит'},
            'body': 'Какая гадость эта ваша заливная рыба!!'
        }]
	return render_template('index.html', user=user, posts=posts) 


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # if POST sent =>
    if form.validate_on_submit():
        # flash sent message in index.html
        flash(f'Login requested for user: {form.username.data}, remember_me: {form.remember_me.data}')
        
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)