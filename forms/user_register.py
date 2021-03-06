from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class UserRegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()], render_kw={'class': 'form-control'})
    surname = StringField('Фамилия', validators=[DataRequired()], render_kw={'class': 'form-control'})
    login = StringField('Логин', validators=[DataRequired()], render_kw={'class': 'form-control'})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    repeat_password = PasswordField('Повторите пароль', validators=[DataRequired()], render_kw={'class': 'form-control'})
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-primary'})
