from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_login import login_required
from decorators.roles import requires_roles
from models.model_user import ModelUser

configuraciones_blueprint = Blueprint('configuraciones', __name__)

class NewRoleForm(FlaskForm):
    description = StringField('Descripcion', validators=[DataRequired()])

@configuraciones_blueprint.route('/administracion_de_roles')
@requires_roles('desarrollador')
def administracion_de_roles():
    form = NewRoleForm()
    try:
        data = ModelUser.get_all_roles()
        return render_template('configuraciones/administracion_de_roles.html', form=form, page_title="Administración de Roles", data=data)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500

@configuraciones_blueprint.route('/crear_rol', methods=['POST'])
@requires_roles('desarrollador')
def crear_rol():
    form = NewRoleForm()
    if form.validate_on_submit():
        description = form.description.data
        new_role, session = ModelUser.new_role(description)
        session.close()

        if new_role is None:
            flash('El rol ya existe o hubo un error en el registro.')
        else:
            flash('Rol creado exitosamente.')

        return redirect(url_for('configuraciones.administracion_de_roles'))

    flash('Error al crear el rol.')
    return redirect(url_for('configuraciones.administracion_de_roles'))

@configuraciones_blueprint.route('/eliminar_rol/<int:id_role>')
@requires_roles('desarrollador')
def delete_role(id_role):
    success, session = ModelUser.delete_role(id_role)
    session.close()

    if success:
        flash('Rol eliminado con éxito.')
    else:
        flash('Error al eliminar el rol.')

    return redirect(url_for('configuraciones.administracion_de_roles'))

@configuraciones_blueprint.route('/editar_rol/<int:id_role>', methods=['POST'])
@requires_roles('desarrollador')
def editar_rol(id_role):
    data = request.get_json()
    new_description = data.get('description')
    if new_description:
        success, session = ModelUser.edit_role(id_role, new_description)
        session.close()

        if success:
            return jsonify({'status': 'success', 'message': 'Rol actualizado con éxito.'})
        else:
            return jsonify({'status': 'error', 'message': 'Error al actualizar el rol.'}), 400

    return jsonify({'status': 'error', 'message': 'Descripción inválida.'}), 400




# <----- Configuracion de Usuarios -----> #
@configuraciones_blueprint.route('/administracion_de_usuarios')
@requires_roles('desarrollador')
def administracion_de_usuarios():
    try:
        data = ModelUser.get_all_users()
        return render_template('configuraciones/administracion_de_usuarios.html', 
                               page_title="Administración de Usuarios", 
                               data=data)  
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    

@configuraciones_blueprint.route('/editar_usuario/<int:user_id>', methods=['POST'])
@requires_roles('desarrollador')
def editar_usuario(user_id):
    data = request.get_json()
    username = data.get('username')
    correo = data.get('correo')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    id_role = data.get('id_role')

    try:
        success, session = ModelUser.edit_user(user_id, username, correo, nombre, apellido, id_role)
        session.close()

        if success:
            return jsonify({'status': 'success', 'message': 'Usuario actualizado con éxito.'})
        else:
            return jsonify({'status': 'error', 'message': 'Error al actualizar el usuario.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    

    



# @compras_blueprint.route('/carro/<int:cart_id>', methods=['GET', 'POST'])
# @requires_roles('desarrollador')
# def carro(cart_id):
#     try:
        
#         data_general = ModelCart.get_cart_detail_by_id(cart_id)[0]
#         data_detail = ModelCart.get_cart_detail_by_id(cart_id)[1]
#         data_resume = resumen_compra(data_detail)
#         print(data_resume['total'])

#         return render_template('carro.html', page_title=f"Carro de Compras", data_detail=data_detail, data_general=data_general, data_resume=data_resume)
#     except Exception as e:
#         print(e)
#         return render_template('error.html'), 500
    
# def resumen_compra(data_detail):
#     cantidad_articulos = len(data_detail)
#     subtotal = sum(item.costo_neto for item in data_detail)
#     impuestos = subtotal * 0.19  # Asumiendo un 19% de impuesto
#     total = subtotal + impuestos

#     return {
#         'cantidad_articulos': cantidad_articulos,
#         'subtotal': subtotal,
#         'impuestos': impuestos,
#         'total': total
#     }

    
# @compras_blueprint.route('/compras')
# @requires_roles('desarrollador')
# def compras():
#     try:
#         data = ModelCart.get_all_carts()
#         return render_template('compras.html', page_title="Compras", data=data)
#     except Exception as e:
#         print(e)
#         return render_template('error.html'), 500
    
    
# @compras_blueprint.route('/eliminar_carro/<int:cart_id>', methods=['POST'])
# @requires_roles('desarrollador')
# def eliminar_carro(cart_id):
#     try:
#         if ModelCart.delete_cart_by_id(cart_id):
#             return jsonify({'success': True}), 200
#         else:
#             return jsonify({'error': 'Carro no encontrado'}), 404
#     except Exception as e:
#         print(e)
#         return jsonify({'error': str(e)}), 500