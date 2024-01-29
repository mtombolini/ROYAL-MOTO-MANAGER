from math import ceil
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from decorators.roles import requires_roles
from models.day_recommendation import DayRecommendation

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/')
def index():
    return redirect(url_for('auth.login'))

@home_blueprint.route('/home', defaults={'page': 1})
@home_blueprint.route('/home/pages/<int:page>')
@requires_roles('desarrollador')
@login_required
def home(page):
    search_query = request.args.get('search', '')
    per_page = 10

    filtered_recommendations = DayRecommendation.filter_recommendations(search_query)

    total_filtered_recommendations = []
    for recommendation in filtered_recommendations:
        if recommendation['recommendation'] != 0:
            total_filtered_recommendations.append(recommendation)

    total_recommendations = len(total_filtered_recommendations)
    
    total_pages = ceil(total_recommendations / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    order_recommendations = sorted(total_filtered_recommendations, key=lambda x: (x['proveedor'], -x['recommendation']))
    recommendations = order_recommendations[start:end]

    if not recommendations:
        return render_template('home.html', recommendations=recommendations, page_title="Inicio", total_pages=total_pages, current_page=page, search_query=search_query)
    
    return render_template('home.html', recommendations=recommendations, page_title="Inicio & Recomendaciones", total_pages=total_pages, current_page=page, search_query=search_query)