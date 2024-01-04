from flask import Blueprint, render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_login import login_user, logout_user

# Modelos y entidades
from models.model_user import ModelUser
from models.user import User

auth_blueprint = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('ConfirmPassword', validators=[DataRequired()])
    correo = StringField('Correo', validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    
@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        logged_user = ModelUser.login(username, password)

        if logged_user is None:
            flash('Usuario no registrado.')
        elif logged_user == False:
            flash('Contraseña inválida.')
        else:
            login_user(logged_user)
            return redirect(url_for('home.home'))

    return render_template('auth/login.html', form=form)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        correo = form.correo.data
        nombre = form.nombre.data
        apellido = form.apellido.data
        id_role = 4  # Asumiendo que se asigna un rol predeterminado

        if password != confirm_password:
            flash('Las contraseñas no coinciden.')
            return render_template('auth/register.html', form=form)

        new_user, session = ModelUser.register(username, password, correo, nombre, apellido, id_role)

        if new_user is None:
            flash('El usuario ya está registrado o hubo un error en el registro.')
            session.close()
        else:
            login_user(new_user)
            session.close()
            return redirect(url_for('home.home'))

    return render_template('auth/register.html', form=form)

@auth_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
