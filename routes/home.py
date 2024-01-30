from math import ceil
from datetime import datetime
from collections import defaultdict

from flask_login import login_required
from flask import Blueprint, render_template, redirect, url_for, request

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
    fecha_hora_actual = datetime.now()
    numero_dia_semana = fecha_hora_actual.weekday()
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    nombre_dia_semana = dias_semana[numero_dia_semana]

    fecha_actual = f"{nombre_dia_semana} {fecha_hora_actual.day}-{fecha_hora_actual.month}-{fecha_hora_actual.year}"

    all_recommendations = []
    all_recom = DayRecommendation.get_all()
    for recom in all_recom:
        if recom['recommendation'] != 0:
            all_recommendations.append(recom)

    number_of_products = 0
    for recommendation in all_recommendations:
        number_of_products += recommendation['recommendation']
            

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

    result = defaultdict(lambda: {'proveedor': '', 'rut': '', 'cantidad_recomendaciones': 0, 'cantidad_productos': 0, 'costo_total': 0.0, 'productos_no_costo': 0})
    for recommendation in all_recommendations:
        proveedor = recommendation['proveedor']
        rut = recommendation['rut']
        cantidad_recomendaciones = recommendation['recommendation']
        costo_producto = recommendation['last_net_cost']['costo_neto']

        result[(proveedor, rut)]['proveedor'] = proveedor
        result[(proveedor, rut)]['rut'] = rut
        result[(proveedor, rut)]['cantidad_recomendaciones'] += 1
        result[(proveedor, rut)]['cantidad_productos'] += cantidad_recomendaciones
        if costo_producto is not None:
            result[(proveedor, rut)]['costo_total'] += cantidad_recomendaciones * costo_producto
        else:
            result[(proveedor, rut)]['costo_total'] += 0.0
            result[(proveedor, rut)]['productos_no_costo'] += 1
    
    supplier_data = list(result.values())
    for supplier in supplier_data:
        supplier['costo_total'] = round(supplier['costo_total'], 1)

    if not recommendations:
        return render_template('home.html', supplier_data=supplier_data, fecha_actual=fecha_actual, total_recommendations=number_of_products, all_recommendations=all_recommendations, recommendations=recommendations, page_title="Inicio", total_pages=total_pages, current_page=page, search_query=search_query)
    
    return render_template('home.html', supplier_data=supplier_data, fecha_actual=fecha_actual, total_recommendations=number_of_products, all_recommendations=all_recommendations, recommendations=recommendations, page_title="Inicio & Recomendaciones", total_pages=total_pages, current_page=page, search_query=search_query)