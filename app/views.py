from datetime import datetime

from app import app
from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm, EditProfileForm
from app.models import User
from flask_login import login_user, current_user, logout_user, login_required
from flask import request
from werkzeug.urls import url_parse
from app.forms import RegistrationForm
from app import db
from app import routes, models, errors
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'nickname': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', posts=posts)
@app.route("/login", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid')
            return redirect(url_for('login'))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc!="":
            next_page = url_for('index')
        return redirect(next_page)
    return render_template("login.html", form = form, title='Sign In')
@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('index'))
@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, email= form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been successfully created!')
        return redirect(url_for('login'))
    return render_template('register.html', form = form, title='Register')
@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    posts = [
        {
            'author': user,
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': user,
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('user.html', user = user, posts = posts)
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated!')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form = form, title='Edit Profile')


