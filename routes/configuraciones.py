from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_login import login_required
from decorators.roles import requires_roles
from models.model_user import ModelUser
from models.supplier import Supplier, CreditTerm
from enum import Enum
from typing import List, Dict
import re

# Regular expression for RUT validation (Chilean tax identification number)
RUT_REGEX = r'^\d{1,2}\.\d{3}\.\d{3}-[0-9kK]$'

configuraciones_blueprint = Blueprint('configuraciones', __name__)

def rut_validator(form: FlaskForm, field: StringField):
    rut = field.data
    if not re.match(RUT_REGEX, rut):
        raise ValidationError('Invalid RUT format')

class NewRoleForm(FlaskForm):
    description = StringField('Descripcion', validators=[DataRequired()])
    
class NewUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    id_role = SelectField('Role', coerce=int, validators=[DataRequired()])
    
class NewSupplierForm(FlaskForm):
    rut = StringField('RUT', validators=[DataRequired(), rut_validator])
    business_name = StringField('Razón Social', validators=[DataRequired()])
    trading_name = StringField('Nombre de Fantasía', validators=[DataRequired()])
    credit_term = SelectField(
        'Plazo de pago', 
        choices=[(term.name, term.value) for term in CreditTerm], 
        validators=[DataRequired()]
    )
    delivery_period = StringField('Tiempo de entrega', validators=[DataRequired()])

@configuraciones_blueprint.route('/administracion_de_roles')
@requires_roles('desarrollador')
def administracion_de_roles():
    form = NewRoleForm()
    try:
        data = ModelUser.get_all_roles()
        return render_template(
            'configuraciones/administracion_de_roles/administracion_de_roles.html', form=form, 
            page_title="Administración de Roles", data=data
        )
    except Exception as e:
        print(e)
        return render_template('error.html'), 500

@configuraciones_blueprint.route('/get_role/<int:role_id>')
@requires_roles('desarrollador')
def get_role(role_id):
    role, _ = ModelUser.get_role_by_id(role_id)
    if role:
        return jsonify(role)
    else:
        return jsonify({'error': 'Role not found'}), 404


@configuraciones_blueprint.route('/crear_rol', methods=['POST'])
@requires_roles('desarrollador')
def crear_rol():
    form = NewRoleForm()
    if form.validate_on_submit():
        description = form.description.data
        new_role, session = ModelUser.new_role(description)
        session.close()

        if new_role is None:
            flash('El rol ya existe o hubo un error en el registro.', 'error')
        else:
            flash('Rol creado exitosamente.', 'success')

        return redirect(url_for('configuraciones.administracion_de_roles'))

    flash('Error al crear el rol.')
    return redirect(url_for('configuraciones.administracion_de_roles'))

@configuraciones_blueprint.route('/eliminar_rol/<int:id_role>')
@requires_roles('desarrollador')
def delete_role(id_role):
    if ModelUser.is_superadmin(id_role)[0]:
        flash('No es posible eliminar el rol superadministrador.', 'error')
    elif ModelUser.role_has_associated_users(id_role)[0]:
        flash('No es posible eliminar un rol con usuarios asociados.', 'error')
    else:
        success, session = ModelUser.delete_role(id_role)
        session.close()

        if success:
            flash('Rol eliminado con éxito.', 'success')
        else:
            flash('Error al eliminar el rol.', 'error')

    return redirect(url_for('configuraciones.administracion_de_roles'))


@configuraciones_blueprint.route('/editar_rol/<int:id_role>', methods=['POST'])
@requires_roles('desarrollador')
def editar_rol(id_role):
    data = request.get_json()
    new_description = data.get('description')

    try:
        if ModelUser.is_superadmin(id_role)[0]:
            response = jsonify({'error': 'No es posible editar el rol "superadministrador".'})
            response.status_code = 403
            return response
    except Exception as e:
        response = jsonify(
            {
                'error': 
                'No se pudo verificar si el rol seleccionado corresponde al superadministrador.'
            }
        )
        response.status_code = 500 # Internal Server Error
        return response

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
    role_data = ModelUser.get_all_roles()  # Fetch roles from database
    form.id_role.choices = [
        (
            role['id_role'], f"{role['id_role']} - {role['description'].capitalize()}"
        ) for role in role_data
    ]
    try:
        data = ModelUser.get_all_users()
        print(data)
        return render_template(
            'configuraciones/administracion_de_usuarios/administracion_de_usuarios.html',
            page_title="Administración de Usuarios", 
            data=data,
            form=form
        )
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    

@configuraciones_blueprint.route('/get_user/<int:user_id>', methods=['GET'])
@requires_roles('desarrollador')
def get_user(user_id):
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
    
    if ModelUser.is_user_the_superadmin(id_user)[0]:
        flash('No es posible eliminar el usuario superadministrador.', 'error')

    else:
        success, session = ModelUser.delete_user(id_user)
        session.close()

        if success:
            flash('Usuario eliminado con éxito.', 'success')
        else:
            flash('Error al eliminar el rol.', 'error')

    return redirect(url_for('configuraciones.administracion_de_usuarios')) 


# <----- Suppliers' Configuration -----> #
@configuraciones_blueprint.route('/suppliers_management')
@requires_roles('desarrollador')
def suppliers_management() -> str:
    form = NewSupplierForm()
    try:
        # Format role data for the SelectField
        data: List[Dict] = Supplier.get_all()
        return render_template('configuraciones/suppliers_management/suppliers_management.html', 
                               page_title="Administración de Proveedores", 
                               data=data,
                               form=form)  
    except Exception as e:
        return render_template('error.html'), 500
    
    
@configuraciones_blueprint.route('/get_supplier/<int:supplier_id>')
@requires_roles('desarrollador')
def get_supplier(supplier_id: int) -> Response:
    try:
        supplier_data: Dict = Supplier.get(supplier_id)
        response = jsonify(supplier_data)
        response.status_code = 200 # Successful
        return response
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while fetching supplier data'})
        response.status_code = 500 # Internal Server Error
        return response
    
    
@configuraciones_blueprint.route('/create_supplier', methods=['POST'])
@requires_roles('desarrollador')
def create_supplier() -> Response:
    form = NewSupplierForm()
    if form.validate_on_submit():
        try:
            rut = form.rut.data
            business_name = form.business_name.data
            trading_name = form.trading_name.data
            credit_term = CreditTerm[form.credit_term.data]
            delivery_period = form.delivery_period.data
            
            new_supplier_data: Dict = \
                Supplier.create(
                    rut=rut, 
                    business_name=business_name,
                    trading_name=trading_name,
                    credit_term=credit_term,
                    delivery_period=delivery_period
                )
            
            new_supplier_data['redirect'] = 'configuraciones.suppliers_management'
            response = jsonify(new_supplier_data)
            response.status_code = 200 # Successful
            return redirect(url_for('configuraciones.suppliers_management'))
        except Exception as ex:
            response = jsonify({'error': str(ex), 
                                'message': 'An error ocurred while creating new supplier',
                                'redirect': 'configuraciones.suppliers_management'})
            response.status_code = 500 # Internal Server Error
            return response
    else:
        # Form validation failed
        errors = {field.name: field.errors for field in form if field.errors}
        response = jsonify({'error': 'Validation failed', 
                            'message': 'Please check the form data',
                            'field errors': errors,
                            'redirect': 'configuraciones.suppliers_management'})
        response.status_code = 400  # Bad Request (validation error)
        return response
    
    
@configuraciones_blueprint.route('/edit_supplier/<int:supplier_id>', methods=['POST'])
@requires_roles('desarrollador')
def edit_supplier(supplier_id: int) -> Response:
    try:
        data = request.get_json()
        rut = data.get('rut')
        business_name = data.get('business_name')
        trading_name = data.get('trading_name')
        credit_term = data.get('credit_term')
        delivery_period = data.get('delivery_period')
        
        if None not in [rut, business_name, trading_name, credit_term, delivery_period]:
            edited_supplier_data: Dict = \
                Supplier.edit(
                    supplier_id, 
                    rut=rut, 
                    business_name=business_name,
                    trading_name=trading_name,
                    credit_term=credit_term,
                    delivery_period=delivery_period
                )
            response = jsonify(edited_supplier_data)
            response.status_code = 200 # Successful
            
            return response
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while editing supplier data'})
        response.status_code = 500 # Internal Server Error
        return response
    

@configuraciones_blueprint.route('/delete_supplier/<int:supplier_id>')
@requires_roles('desarrollador')
def delete_supplier(supplier_id: int) -> Response:
    try:
        Supplier.delete(supplier_id)
        response = jsonify({'status': 'success', 'message': 'Proveedor eliminado con éxito.'})
        response.status_code = 200 # Successful
        return redirect(url_for('configuraciones.suppliers_management'))
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while deleting supplier'})
        response.status_code = 500 # Internal Server Error
        return response
        
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
