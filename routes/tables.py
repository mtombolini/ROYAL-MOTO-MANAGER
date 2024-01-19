from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from models.productos import Product, ProductStock
from models.reception import Reception, ReceptionDetail
from databases.session import AppSession
from urllib.parse import urlencode

tables_blueprint = Blueprint('tables', __name__)

@tables_blueprint.route('/productos')
def get_products():
    products = Product.get_all_products()
    return render_template('tables/products.html', products=products, page_title="Productos")

@tables_blueprint.route("/productos/<variant_id>")
def product_detail(variant_id):
    product, prediction = Product.filter_product(variant_id)

    return render_template("tables/product_detail.html", product=product, variant_id=variant_id, prediction=prediction, page_title=f"{product['description']}")

