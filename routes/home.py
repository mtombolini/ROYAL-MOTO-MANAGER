from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from decorators.roles import requires_roles
from models.day_recommendation import DayRecommendation

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/')
def index():
    return redirect(url_for('auth.login'))

@home_blueprint.route('/home')
@requires_roles('desarrollador')
@login_required
def home():
    day_recommendations = DayRecommendation.get_all()
    if not day_recommendations:
        return render_template('home.html', recommendations=day_recommendations, page_title="Inicio")
    return render_template('home.html', recommendations=day_recommendations, page_title="Inicio & Recomendaciones")