from datetime import datetime
from html import unescape

from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required
from decorators.roles import requires_roles

from models.cart import BuyCart, BuyCartDetail
from models.user import User
from models.model_cart import ModelCart

compras_blueprint = Blueprint('compras', __name__)

@compras_blueprint.route('/stock_critico')
@requires_roles('desarrollador')
def stock_critico():
    return render_template('home.html', page_title="Stock Crítico")

@compras_blueprint.route('/carro/<int:cart_id>', methods=['GET', 'POST'])
@requires_roles('desarrollador')
def carro(cart_id):
    try:
        data_general = ModelCart.get_cart_detail_by_id(cart_id)[0]
        data_detail = ModelCart.get_cart_detail_by_id(cart_id)[1]
        data_resume = resumen_compra(data_general)

        return render_template('carro.html', page_title=f"Carro de Compras", data_detail=data_detail, data_general=data_general, data_resume=data_resume)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    
def resumen_compra(data_general):
    cantidad_articulos = data_general.cantidad_productos
    subtotal = data_general.monto_neto
    impuestos = subtotal * 0.19  # Asumiendo un 19% de impuesto
    total = subtotal + impuestos

    return {
        'cantidad_articulos': cantidad_articulos,
        'subtotal': subtotal,
        'impuestos': impuestos,
        'total': total
    }

    
@compras_blueprint.route('/compras')
@requires_roles('desarrollador')
def compras():
    try:
        data = ModelCart.get_all_carts()
        return render_template('compras.html', page_title="Compras", data=data)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    
    
@compras_blueprint.route('/eliminar_carro/<int:cart_id>')
@requires_roles('desarrollador')
def eliminar_carro(cart_id):
    try:
        if ModelCart.delete_cart_by_id(cart_id):
            return redirect(url_for('compras.compras'))
        else:
            return jsonify({'error': 'Carro no encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@compras_blueprint.route('/eliminar_producto_carro/<int:cart_id>/<int:cart_detail_id>/<int:products_quantity>')
@requires_roles('desarrollador')
def eliminar_producto(cart_id, cart_detail_id, products_quantity):
    try:
        if products_quantity == 1:
            return redirect(url_for('compras.eliminar_carro', cart_id=cart_id))
        elif ModelCart.delete_cart_detail_by_id(cart_detail_id):
            return redirect(url_for('compras.carro', cart_id=cart_id))
        else:
            return jsonify({'error': 'Producto no encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@compras_blueprint.route('/compras', methods=['POST'])
@requires_roles('desarrollador')
def agregar_producto():
    try:
        data = request.json
        product = data['product']
        cantidad = int(data['cantidad'])

        product['description'] = unescape(product['description'])
        product['last_net_cost'] = float(product['last_net_cost'])

        carts = ModelCart.get_all_carts()
        existing_cart = next((cart for cart in carts if cart.proveedor == product['supplier']), None)

        if existing_cart:
            cart = existing_cart
        else:
            cart_data = {
                'descripcion': "Descripción Pendiente",
                'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'proveedor': product['supplier'],
                'monto_neto': 0,
                'cantidad_productos': 0,
                'estado': "Creado",
                'revision': "Pendiente",
                'rendimiento': "Pendiente"
            }

            cart = ModelCart.create_cart(cart_data)

        detail_data = {
            'cart_id': cart.cart_id,
            'variant_id': product['variant_id'],
            'descripcion_producto': product['description'],
            'sku_producto': product['sku'],
            'costo_neto': product['last_net_cost'],
            'cantidad': cantidad
        }

        ModelCart.create_cart_detail(detail_data)

        suma_monto = product['last_net_cost'] * cantidad
        suma_cantidad = cantidad

        ModelCart.update_cart(cart.cart_id, int(suma_monto), suma_cantidad)

        carts = ModelCart.get_all_carts()
        return jsonify({'redirect': url_for('compras.compras')})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compras_blueprint.route('/actualizar_producto_carro', methods=['POST'])
@requires_roles('desarrollador')
def actualizar_producto_carro():
    try:
        cantidad = request.json['cantidad']
        cart_detail_id = request.json['cart_detail_id']
        cart_id = request.json['cart_id']
        
        ModelCart.update_cart_detail(cart_detail_id, cantidad)
        ModelCart.check_to_update_all_cart(cart_id)
        return jsonify({'redirect': url_for('compras.carro', cart_id=cart_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
