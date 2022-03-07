import os
import datetime

from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_required, logout_user, current_user, login_user

from data import db_session

from forms.user_register import UserRegisterForm
from forms.restaurant_register import RestaurantRegisterForm
from forms.login import LoginForm

from data.models.profile_types import ProfileType
from data.models.users import User
from data.models.restaurants import Restaurant
from data.models.menus import Menu


# Will not work on Heroku, but needed for tests
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)


def abort_if_restaurant():
    if current_user.__class__.__name__ == 'Restaurant':
        abort(403)


def abort_if_user():
    if current_user.__class__.__name__ == 'User':
        abort(403)


@app.errorhandler(403)
def forbidden_error():
    return render_template('bad_account_type.html')


# User load
@login_manager.user_loader
def load_user(profile_id):
    db_sess = db_session.create_session()
    profile = db_sess.query(ProfileType).get(profile_id)
    if not profile:
        return profile
    if profile.profile_type == 'User':
        return db_sess.query(User).get(profile.account_id)
    if profile.profile_type == 'Restaurant':
        return db_sess.query(Restaurant).get(profile.account_id)


# Register
@app.route('/user_register', methods=['POST', 'GET'])
def user_register():
    form = UserRegisterForm()
    additional_link = {
        'link': '/restaurant_register',
        'label': 'Регистрация для ресторана'
    }
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('user_register.html', title='Регистрация пользователя', form=form, additional_link=additional_link)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('user_register.html', title='Регистрация пользователя', form=form, additional_link=additional_link)
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            login=form.login.data
        )
        user.set_password(form.password.data)
        profile = ProfileType(
            profile_type=user.__class__.__name__,
            account_id=user.id
        )
        db_sess.add(user)
        db_sess.add(profile)
        db_sess.commit()
        profile.account_id = user.id
        user.profile_id = profile.id
        db_sess.commit()
    return render_template('form.html', title='Регистрация пользователя', form=form, additional_link=additional_link)


@app.route('/restaurant_register', methods=['POST', 'GET'])
def restaurant_register():
    form = RestaurantRegisterForm()
    additional_link = {
        'link': '/user_register',
        'label': 'Регистрация для пользователя'
    }
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            form.repeat_password.errors.append('Пароли не совпадают')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form, additional_link=additional_link)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.login == form.login.data).first():
            form.login.errors.append('Этот логин занят')
            return render_template('restaurant_register.html', title='Регистрация ресторана', form=form, additional_link=additional_link)
        restaurant = Restaurant(
            title=form.title.data,
            login=form.login.data
        )
        profile = ProfileType(
            profile_type=restaurant.__class__.__name__,
            account_id=restaurant.id
        )
        restaurant.profile_id = profile.id
        restaurant.set_password(form.password.data)
        menu = Menu()
        db_sess.add(menu)
        db_sess.add(profile)
        menu.restaurant.append(restaurant)
        db_sess.commit()
    return render_template('form.html', title='Регистрация ресторана', additional_link=additional_link, form=form)


# Login
@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    additional_link = {
        'link': '/restaurant_login',
        'label': 'Авторизация для ресторана'
    }
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.account_id == user.profile_id).first()
            login_user(profile, remember=form.remember_me.data)
            return redirect("/")
        errors = ['Неправильный логин или пароль']
        return render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link, errors=errors)
    return render_template('form.html', title='Авторизация пользователя', form=form, additional_link=additional_link)


@app.route('/restaurant_login', methods=['GET', 'POST'])
def restaurant_login():
    form = LoginForm()
    additional_link = {
        'link': 'user_login',
        'label': 'Авторизация для пользователя'
    }
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        restaurant = db_sess.query(User).filter(Restaurant.login == form.login.data).first()
        if restaurant and restaurant.check_password(form.password.data):
            profile = db_sess.query(ProfileType).filter(ProfileType.account_id == restaurant.profile_id).first()
            login_user(profile, remember=form.remember_me.data)
            return redirect("/")
        return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link, errors=['Неправильный логин или пароль'])
    return render_template('form.html', title='Авторизация ресторана', form=form, additional_link=additional_link)


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Main page
@app.route('/')
def main_page():
    return render_template('main_page.html', title='Order anywhere')


if __name__ == '__main__':
    db_session.global_init(os.environ.get('DATABASE_URL'))
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
