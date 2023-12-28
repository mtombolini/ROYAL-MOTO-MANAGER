from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required
from decorators.roles import requires_roles

# Modelos y entidades
from models.cart import BuyCart
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
        data_resume = resumen_compra(data_detail)
        print(data_resume['total'])

        return render_template('carro.html', page_title=f"Carro de Compras", data_detail=data_detail, data_general=data_general, data_resume=data_resume)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    
def resumen_compra(data_detail):
    cantidad_articulos = len(data_detail)
    subtotal = sum(item.costo_neto for item in data_detail)
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
    
@compras_blueprint.route('/eliminar_carro/<int:cart_id>', methods=['POST'])
@requires_roles('desarrollador')
def eliminar_carro(cart_id):
    try:
        if ModelCart.delete_cart_by_id(cart_id):
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Carro no encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
