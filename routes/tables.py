from math import ceil
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models.productos import Product, ProductStock
from models.reception import Reception, ReceptionDetail
from databases.session import AppSession
from urllib.parse import urlencode

tables_blueprint = Blueprint('tables', __name__)

@tables_blueprint.route('/productos', defaults={'page': 1})
@tables_blueprint.route('/productos/pages/<int:page>')
def get_products(page):
    search_query = request.args.get('search', '')
    per_page = 75

    filtered_products = Product.filter_products(search_query)

    total_products = len(filtered_products)
    total_pages = ceil(total_products / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    products = filtered_products[start:end]
    
    return render_template('tables/products.html', products=products, page_title="Productos", total_pages=total_pages, current_page=page, search_query=search_query)

@tables_blueprint.route("/productos/<variant_id>")
def product_detail(variant_id):
    product, prediction = Product.filter_product(variant_id)
    return render_template("tables/product_detail.html", product=product, variant_id=variant_id, prediction=prediction, page_title=f"{product['description']}")

