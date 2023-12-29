from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from decorators.roles import requires_roles


home_blueprint = Blueprint('home', __name__)

# @requires_roles('desarrollador')
# @home_blueprint.route('/')
# def index():
#     return redirect(url_for('auth.login'))


@home_blueprint.route('/home')
@requires_roles('desarrollador')
@login_required
def home():
    return render_template('home.html', page_title="Inicio")


