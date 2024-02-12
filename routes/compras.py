from datetime import datetime
from html import unescape
from app.config import TOKEN

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, flash
from flask_login import login_required
from decorators.roles import requires_roles

from api.search.product_search import ProductSearch

from models.cart import BuyCart, BuyCartDetail
from models.user import User
from models.model_cart import ModelCart
from models.productos import Product
from models.pay_dates import PayDates

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
    cantidad_articulos = round(data_general.cantidad_productos, 2)
    subtotal = round(data_general.monto_neto, 2)
    impuestos = round(subtotal * 0.19, 2)  # Asumiendo un 19% de impuesto
    total = round(subtotal + impuestos, 2)

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
    
@compras_blueprint.route('/eliminar_producto_carro/<int:cart_id>/<int:cart_detail_id>/<int:products_quantity>/<state>')
@requires_roles('desarrollador')
def eliminar_producto(cart_id, cart_detail_id, products_quantity, state):
    try:
        if products_quantity == 1:
            return redirect(url_for('compras.eliminar_carro', cart_id=cart_id))
        
        elif state == "Creado":
            if ModelCart.delete_cart_detail_by_id(cart_detail_id):
                ModelCart.check_to_update_all_cart(cart_id)
                return redirect(url_for('compras.carro', cart_id=cart_id))
        
        elif state == "Emitida":
            if ModelCart.delete_cart_detail_by_id(cart_detail_id):
                ModelCart.check_to_update_all_cart(cart_id)
                return redirect(url_for('compras.recepcionar_carro_compra', cart_id=cart_id))
            
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
        existing_carts = [cart for cart in carts if cart.proveedor == product['supplier'] and cart.estado == "Creado"]

        if existing_carts:
            cart = existing_carts[0]
        else:
            cart_data = {
                'descripcion': "Descripción Pendiente",
                'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fecha_recepcion': "-",
                'proveedor': product['supplier'],
                'rut': product['rut'],
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
        data = request.json
        costo_neto = data['costo']
        cantidad = data['cantidad']
        cart_detail_id = data['cart_detail_id']
        cart_id = data['cart_id']
        
        ModelCart.update_cart_detail(cart_detail_id, cantidad, costo_neto)
        ModelCart.check_to_update_all_cart(cart_id)
        return jsonify({'redirect': url_for('compras.carro', cart_id=cart_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compras_blueprint.route('/emitir_compra', methods=['POST'])
@requires_roles('desarrollador')
def emitir_compra():
    try:
        data = request.json
        general_data = data['general']

        ModelCart.update_cart_status(general_data['cartId'], "Emitida")

        return jsonify({'redirect': url_for('compras.carro', cart_id=general_data['cartId'])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@compras_blueprint.route('/recepcionar_carro_compra/<int:cart_id>')
@requires_roles('desarrollador')
def recepcionar_carro_compra(cart_id):
    try:
        data_general = ModelCart.get_cart_detail_by_id(cart_id)[0]
        data_detail = ModelCart.get_cart_detail_by_id(cart_id)[1]
        data_resume = resumen_compra(data_general)

        return render_template('recepcion_compra.html', page_title="Recepción", data_detail=data_detail, data_general=data_general, data_resume=data_resume)
    except Exception as e:
        return render_template('error.html'), 500
    
@compras_blueprint.route('/agregar_producto_recepcion/<int:cart_id>')
@requires_roles('desarrollador')
def agregar_producto_recepcion(cart_id):
    try:
        search_query = request.args.get('search', '')
        product, rut, last_net_cost = Product.product_filter_by_sku(search_query)
        continue_search = True
        api_call = False
        if product is None:
            product_search = ProductSearch(TOKEN)
            product_data = product_search.get_data(search_query)

            if product_data is None or product_data['count'] == 0:
                continue_search = False
                flash('Producto no encontrado', 'error')
            else:
                api_call = True
                continue_search = True

        if continue_search and not api_call:
            if rut != ModelCart.get_cart_detail_by_id(cart_id)[0].rut:
                flash('Producto no corresponde al proveedor', 'error')
            else:
                detail_data = {
                    'cart_id': cart_id,
                    'variant_id': product.variant_id,
                    'descripcion_producto': unescape(product.description),
                    'sku_producto': product.sku,
                    'costo_neto': float(last_net_cost),
                    'cantidad': 1
                }
                ModelCart.create_cart_detail(detail_data)

                suma_monto = detail_data['costo_neto'] * 1
                suma_cantidad = 1

                ModelCart.update_cart(cart_id, int(suma_monto), suma_cantidad)

        elif continue_search and api_call:
            detail_data = {
                'cart_id': cart_id,
                'variant_id': product_data['variant id'],
                'descripcion_producto': unescape(product_data['description']),
                'sku_producto': product_data['sku'],
                'costo_neto': float(1),
                'cantidad': 1
            }

            ModelCart.create_cart_detail(detail_data)

            suma_monto = detail_data['costo_neto'] * 1
            suma_cantidad = 1

            ModelCart.update_cart(cart_id, int(suma_monto), suma_cantidad)

    except Exception as e:
        return render_template('error.html'), 500
    finally:
        return redirect(url_for('compras.recepcionar_carro_compra', cart_id=cart_id))
    
@compras_blueprint.route('/obtener_fechas_de_pago/<int:cart_id>', methods=['GET'])
@requires_roles('desarrollador')
def get_paydates(cart_id):
    pay_dates = PayDates.get_pay_dates(cart_id)
    dates = [pay_date.fecha_pago.strftime('%Y-%m-%d') for pay_date in pay_dates]
    return jsonify(dates)

@compras_blueprint.route('/actualizar_fechas_de_pago/<int:cart_id>/<state>', methods=['POST'])
def update_paydates(cart_id, state):
    try:
        dates = request.json['dates']
        
        PayDates.delete_existing_dates(cart_id)

        PayDates.create_new_dates(cart_id, dates)
        flash('Fechas de pago actualizadas', 'success')
        if state == 'emitida':
            return jsonify({'status': 'success', 'redirect': url_for('compras.carro', cart_id=cart_id)})
        else:
            return jsonify({'status': 'success', 'redirect': url_for('compras.recepcionar_carro_compra', cart_id=cart_id)})
        
    except Exception as e:
        flash('Error al actualizar fechas de pago', 'error')
        if state == 'emitida':
            return jsonify({'error': str(e), 'redirect': url_for('compras.carro', cart_id=cart_id)}), 500
        else:
            return jsonify({'error': str(e), 'redirect': url_for('compras.recepcionar_carro_compra', cart_id=cart_id)}), 500
