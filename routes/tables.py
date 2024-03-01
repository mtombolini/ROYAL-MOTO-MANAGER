from math import ceil
from json import dumps
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from models.productos import Product, ProductStock
from models.supplier import Supplier
from models.reception import Reception, ReceptionDetail
from databases.session import AppSession
from urllib.parse import urlencode

tables_blueprint = Blueprint('tables', __name__)

@tables_blueprint.route('/productos', defaults={'page': 1})
@tables_blueprint.route('/productos/pages/<int:page>')
def get_products(page):
    current_search_query = request.args.get('search', '')

    if 'search_query' not in session or current_search_query != session.get('search_query'):
        session['search_query'] = current_search_query
        if current_search_query and page != 1:
            return redirect(url_for('tables.get_products', search=current_search_query, page=1))
    else:
        if page < 1:
            page = 1

    filtered_products = Product.filter_products(session.get('search_query', ''))

    per_page = 75
    total_products = len(filtered_products)
    total_pages = ceil(total_products / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    products = filtered_products[start:end]

    return render_template('tables/products.html', products=products, page_title="Productos", total_pages=total_pages, current_page=page, search_query=session.get('search_query', ''))

@tables_blueprint.route("/productos/<variant_id>")
def product_detail(variant_id):
    product, prediction = Product.filter_product(variant_id)
    suppliers = Supplier.get_all_class()
    data_supplier = {}
    for supplier in suppliers:
        data_supplier[supplier.id] = supplier.trading_name
    data_supplier_json = dumps(data_supplier)

    if product['stock']['stock_lira'] + product['stock']['stock_sobrexistencia'] != product['kardex'][-1]['stock_actual']:
        flash("CUIDADO: El stock actual no coincide con el último registro del kardex", "warning")

    return render_template("tables/product_detail.html", product=product, variant_id=variant_id, prediction=prediction, page_title=f"{product['description']}", all_suppliers=data_supplier_json)

@tables_blueprint.route("/productos/<variant_id>/cambio_proveedor", methods=["POST"])
def change_supplier(variant_id):
    try:
        data = request.get_json()

        supplier_id = int(data.get('supplierId'))
        supplier_name = data.get('supplierName')

        Product.update_product_supplier(variant_id, supplier_id)

        return jsonify({'success': True, 'message': 'Proveedor actualizado correctamente.', 'redirect': url_for('tables.product_detail', variant_id=variant_id)})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error al actualizar el proveedor.'}), 500