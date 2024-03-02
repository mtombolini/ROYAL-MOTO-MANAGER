from datetime import datetime
import json
from html import unescape
from app.config import TOKEN
import os
import pdfkit
import base64

from flask import Blueprint, render_template, redirect, url_for, jsonify, request, flash, send_file, current_app
from flask_login import login_required
from decorators.roles import requires_roles
from reportlab.pdfgen import canvas
from io import BytesIO

from api.get.product_search import ProductSearch
from api.post.reception_post import ReceptionPost

from models.user import User
from models.office import Office
from models.productos import Product
from models.pay_dates import PayDates
from models.model_cart import ModelCart
from models.cart import BuyCart, BuyCartDetail
from services.analysis.buys_analisys import BuysAnalysis

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

        if product['last_net_cost'] == "None":
            product['last_net_cost'] = 1.0

        product['description'] = unescape(product['description'])
        product['last_net_cost'] = float(product['last_net_cost'])

        carts = ModelCart.get_all_carts()
        existing_carts = [cart for cart in carts if cart.proveedor == product['supplier'] and cart.estado == "Creado"]
        print(existing_carts)
        if existing_carts:
            cart = existing_carts[0]
        else:
            cart_data = {
                'descripcion': "Descripción Pendiente",
                'fecha_creacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'fecha_recepcion': "-",
                'proveedor': product['supplier'],
                'rut': product['rut'],
                'razon_social': product['social_reason'],
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
        offices_info = Office.get_all_offices()
        pay_dates_len = len(PayDates.get_pay_dates(cart_id))

        return render_template('recepcion_compra.html', page_title="Recepción", data_detail=data_detail, data_general=data_general, data_resume=data_resume, offices=offices_info, pay_dates_len=pay_dates_len)
    except Exception as e:
        return render_template('error.html'), 500
    
@compras_blueprint.route('/agregar_producto_recepcion/<int:cart_id>')
@requires_roles('desarrollador')
def agregar_producto_recepcion(cart_id):
    try:
        search_query = request.args.get('search', '')
        product, rut, last_net_cost = Product.product_filter_by_sku(search_query)

        if last_net_cost == None:
            last_net_cost = 1.0

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
        
@compras_blueprint.route('/procesar_datos_recepcion', methods=['POST'])
def procesar_datos_recepcion():
    try:
        datos_recibidos = dict(request.get_json())
        cart_id = datos_recibidos['cartId']

        document = datos_recibidos['tipoDocumentoValue']
        officeId = int(datos_recibidos['sucursalValue'])
        business_name_limitado = datos_recibidos['businessName'][:85]
        note = f"{business_name_limitado} / {datos_recibidos['rut']}"
        documentNumber = datos_recibidos['numerosFolios']
        numberList = datos_recibidos['listaFolios']

        all_data_post = []
        for folio in numberList:
            details = []
            for product in datos_recibidos['productos']:
                if product['folio'] == folio:
                    details.append({
                        'quantity': product['cantidad'],
                        'variantId': product['variantId'],
                        'cost': float(product['costo_real'])
                    })

            data_post = {
                'document': document,
                'officeId': officeId,
                'documentNumber': folio,
                'note': note,
                'details': details
            }

            all_data_post.append(data_post)

        responses = []
        for data_post in all_data_post:
            reception_post = ReceptionPost(TOKEN)
            response = reception_post.send_data(data_post)

            responses.append(response)

        for product in datos_recibidos['productos']:
            cart_detail_id = product['id']
            cantidad = product['cantidad']
            costo_neto = product['costo_real']

            ModelCart.update_cart_detail(cart_detail_id, cantidad, costo_neto)

        ModelCart.check_to_update_all_cart(cart_id)
        ModelCart.update_cart_status(cart_id, "Recepcionada")
        ModelCart.update_cart_datatime(cart_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # if None in responses:
        #     raise
        return jsonify({"mensaje": "Datos recibidos correctamente", "redirect": url_for('compras.carro', cart_id=cart_id)})
        
    except Exception as e:
        return jsonify({"error": str(e), "redirect": url_for('compras.recepcionar_carro_compra', cart_id=cart_id)}), 500
    
@compras_blueprint.route('/generar-pdf-recepcion', methods=['POST'])
def generar_pdf():
    data = request.json
    logo_path = os.path.join(current_app.root_path, 'static\\img\\logo_invert.png')
    logo_path = logo_path.replace('\\app\\', '\\')

    with open(logo_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode()

    general_data = data['general'].split(';')
    resume_data = data['resume'].split(';')
    detail_data = [d.split('|') for d in data['detail'].split(', ')[:-1]]

    general = {
        "id": general_data[0],
        "descripcion": general_data[1],
        "proveedor": general_data[2],
        "fecha_creacion": general_data[3],
        "estado": general_data[4],
    }

    resume = {
        "cantidad_items": resume_data[0],
        "cantidad_detalles": resume_data[1],
        "subtotal": resume_data[2],
        "impuestos": resume_data[3],
        "total": resume_data[4]
    }

    html = render_template('pdfs/emition_pdf.html', general_data=general, resume_data=resume, detail_data=detail_data, image_base64=image_base64)

    options = {
        'footer-right': '[page]',
        'page-size': 'Letter'
    }

    pdf = pdfkit.from_string(html, False, options=options)

    buffer = BytesIO(pdf)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='archivo.pdf', mimetype='application/pdf')

@compras_blueprint.route('/rendimiento_compra/<int:cart_id>')
def rendimiento_compra(cart_id):
    try:
        data_general = ModelCart.get_cart_detail_by_id(cart_id)[0]
        data_cart_general = {
            "fecha_recepcion": data_general.fecha_recepcion,
            "proveedor": data_general.proveedor,
            "rut": data_general.rut,
            "cantidad_productos": data_general.cantidad_productos,
            "monto_neto": data_general.monto_neto
        }
        buys_analysis = BuysAnalysis(cart_id)
        buys_analysis.create_info()

        purchase_margin = buys_analysis.calculate_net_margin_per_purchase()
        margin_product_info = buys_analysis.calculate_net_margin_per_product()
        sales_evaluation = buys_analysis.evaluate_sales_by_payment_term()

        json_barras = buys_analysis.create_barras_apiladas(purchase_margin[cart_id])
        json_barra_progreso = buys_analysis.barra_progreso(sales_evaluation[cart_id])
        json_productos_barras_progreso = buys_analysis.productos_barras_progreso(sales_evaluation[cart_id])
        json_roi_por_productos = buys_analysis.roi_por_productos(margin_product_info)
        json_breakeven_de_compra = buys_analysis.breakeven_de_compra(purchase_margin[cart_id], margin_product_info, sales_evaluation[cart_id])
        json_dist_cantidad, json_dist_costo, json_dist_venta_max, json_dist_venta_hoy = buys_analysis.distribuciones_productos(margin_product_info)

        return render_template('rendimiento_compra.html', page_title="Rendimiento de Compra", cart_id=cart_id, json_barras=json_barras, json_barra_progreso=json_barra_progreso, json_roi_por_productos=json_roi_por_productos, json_breakeven_de_compra=json_breakeven_de_compra, json_dist_cantidad=json_dist_cantidad, json_dist_costo=json_dist_costo, json_dist_venta_max=json_dist_venta_max, json_dist_venta_hoy=json_dist_venta_hoy, json_productos_barras_progreso=json_productos_barras_progreso, data_cart_general=data_cart_general)
    
    except Exception as e:
        return render_template('error.html'), 500