from flask import Blueprint, render_template, redirect, url_for, flash, session, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_login import login_user, logout_user, current_user, login_required

# Modelos y entidades
from models.model_user import ModelUser
from models.user import User
import os

auth_blueprint = Blueprint('auth', __name__, template_folder='../templates')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data  # Obtiene el nombre de usuario del formulario
        password = form.password.data  # Obtiene la contraseña del formulario

        logged_user = ModelUser.login(username, password)  # Inicia sesión con esos datos

        if logged_user is None:
            flash('Usuario no registrado.')
        elif logged_user == False:
            flash('Contraseña inválida.')
        else:
            login_user(logged_user)
            return redirect(url_for('home.home'))

    return render_template('auth/login.html', form=form)


@auth_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

