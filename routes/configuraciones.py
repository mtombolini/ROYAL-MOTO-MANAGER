from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, Email
from flask_login import login_required
from decorators.roles import requires_roles
from models.model_user import ModelUser

configuraciones_blueprint = Blueprint('configuraciones', __name__)

class NewRoleForm(FlaskForm):
    description = StringField('Descripcion', validators=[DataRequired()])
    
    
class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    id_role = IntegerField('ID Role', validators=[DataRequired()])

@configuraciones_blueprint.route('/administracion_de_roles')
@requires_roles('desarrollador')
def administracion_de_roles():
    form = NewRoleForm()
    try:
        data = ModelUser.get_all_roles()
        print(data)
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
    # Verificar que no estemos eliminando el superadmin
    try:
        if ModelUser.is_superadmin(id_role)[0]:
            return jsonify({'status': 'error', 'message': 'No es posible eliminar el rol "superadministrador".'}), 403
        elif ModelUser.role_has_associated_users(id_role)[0]:
            return jsonify({'status': 'error', 'message': 'No es posible eliminar un rol con usuarios asociados.'}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
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

    # Obtener la descripción actual del rol desde la base de datos
    try:
        if ModelUser.is_superadmin(id_role)[0]:
            return jsonify({'status': 'error', 'message': 'No es posible editar el rol "superadministrador".'}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

    # Continuar con la edición si la descripción actual no es 'superadministrador'
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
    form = NewUserForm()
    try:
        data = ModelUser.get_all_users()
        print(data)
        return render_template('configuraciones/administracion_de_usuarios.html', 
                               page_title="Administración de Usuarios", 
                               data=data,
                               form=form)  
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    

@configuraciones_blueprint.route('/get_user/<int:user_id>', methods=['GET'])
@requires_roles('desarrollador')  # Adjust the role requirement as needed
def get_user(user_id):
    print("user_id", user_id)
    try:
        user = ModelUser.get_by_id(user_id)
        if user:
            # Convert the user object to a dictionary
            user_data = {
                'id': user.id,
                'username': user.username,
                'correo': user.correo,
                'nombre': user.nombre,
                'apellido': user.apellido,
                'id_role': user.id_role,
            }
            print(jsonify(user_data))
            return jsonify(user_data)
        else:
            return jsonify({'status': 'error', 'message': 'Usuario no encontrado'}), 404
    except Exception as e:
        print(e)  # Consider using logging instead of print for production code
        return jsonify({'status': 'error', 'message': str(e)}), 500


@configuraciones_blueprint.route('/editar_usuario/<int:user_id>', methods=['POST'])
@requires_roles('desarrollador')
def editar_usuario(user_id):
    data = request.get_json()
    
    print(data)
    username = data.get('username')
    print(username)
    correo = data.get('email')
    print(correo)
    nombre = data.get('first_name')
    apellido = data.get('last_name')
    id_role = data.get('id_role')

    # Verifica si el nombre de usuario es 'superuser'
    if username.lower() == 'superadmin':
        return jsonify({'status': 'error', 'message': 'No es posible editar el usuario "superuser".'}), 403
    
    try:
        success, session = ModelUser.edit_user(user_id, username, correo, nombre, apellido, id_role)
        session.close()

        if success:
            return jsonify({'status': 'success', 'message': 'Usuario actualizado con éxito.'})
        else:
            return jsonify({'status': 'error', 'message': 'Error al actualizar el usuario.'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@configuraciones_blueprint.route('/eliminar_usuario/<int:id_user>')
@requires_roles('desarrollador')
def eliminar_usuario(id_user):
    # Verificar que no estemos eliminando el superadmin
    try:
        if ModelUser.is_user_the_superadmin(id_user)[0]:
            return jsonify({'status': 'error', 'message': 'No es posible eliminar usuario con el rol de "superadministrador".'}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    success, session = ModelUser.delete_user(id_user)
    session.close()

    if success:
        flash('Rol eliminado con éxito.')
    else:
        flash('Error al eliminar el rol.')

    return redirect(url_for('configuraciones.administracion_de_usuarios')) 



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
