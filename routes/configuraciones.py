from __future__ import annotations
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, HiddenField, Field
from wtforms.validators import DataRequired, Length, Email, ValidationError
from flask_login import login_required
from decorators.roles import requires_roles
from models.model_user import ModelUser
from models.supplier import Supplier, CreditTerm
from enum import Enum
from io import BytesIO
import pandas as pd
from typing import List, Dict, Tuple
import re


configuraciones_blueprint = Blueprint('configuraciones', __name__)

# ------------------------- FORMATTING FUNCTIONS ------------------------- #
def format_rut(rut: str) -> str:        
    rut = rut.replace('.', '').replace('-', '')  # Remove existing formatting
    body, verifier = rut[:-1], rut[-1]  # Split into body and verifier
    formatted_body = '.'.join([body[max(i-3, 0):i] for i in range(len(body), 0, -3)][::-1])
    return f"{formatted_body}-{verifier}"

def format_supplier_data_for_database(form: SupplierForm) -> Tuple:
    rut = format_rut(form.rut.data)
    business_name = form.business_name.data.upper()
    trading_name = form.trading_name.data
    credit_term = CreditTerm[form.credit_term.data]
    delivery_period = form.delivery_period.data
    return rut, business_name, trading_name, credit_term, delivery_period

def format_suppliers_data_for_render(suppliers_data: List[Dict | None]) -> List[Dict | None]:
    for supplier in suppliers_data:
        supplier['credit_term'] = supplier['credit_term'].value
    return suppliers_data

class NoRUTDuplicateValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        print(Supplier.get_all())
        for supplier in Supplier.get_all():
            if format_rut(field.data) == supplier['rut'] and form.id.data != supplier['id']:
                raise ValidationError("There is already a supplier with this RUT.")

# ------------------------- FORMS ------------------------- #
class RoleForm(FlaskForm):
    description = StringField('Descripcion', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    id_role = SelectField('Role', coerce=int, validators=[DataRequired()])

class SupplierForm(FlaskForm):
    id = HiddenField('ID de proveedor')
    rut = StringField('RUT', validators=[DataRequired(), NoRUTDuplicateValidator()])
    business_name = StringField('Razón Social', validators=[DataRequired()])
    trading_name = StringField('Nombre de Fantasía', validators=[DataRequired()])
    credit_term = SelectField(
        'Plazo de pago', 
        choices=[(term.name, term.value) for term in CreditTerm], 
        validators=[DataRequired()]
    )
    delivery_period = StringField('Tiempo de entrega', validators=[DataRequired()])

# ------------------------- ROLE ROUTES ------------------------- #
@configuraciones_blueprint.route('/administracion_de_roles')
@requires_roles('desarrollador')
def administracion_de_roles():
    form = RoleForm()
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
    form = RoleForm()
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
            flash('Rol actualizado con éxito.', 'success')
            return jsonify({'status': 'success', 'message': 'Rol actualizado con éxito.', 'redirect': url_for('configuraciones.administracion_de_roles')})
        else:
            flash('Error al actualizar el rol.', 'error')
            return jsonify({'status': 'error', 'message': 'Error al actualizar el rol.', 'redirect': url_for('configuraciones.administracion_de_roles')}), 400

    return jsonify({'status': 'error', 'message': 'Descripción inválida.', 'redirect': url_for('configuraciones.administracion_de_roles')}), 400

# ------------------------- USER ROUTES ------------------------- #
@configuraciones_blueprint.route('/administracion_de_usuarios')
@requires_roles('desarrollador')
def administracion_de_usuarios():
    form = UserForm()
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
    username = data.get('username')
    correo = data.get('email')
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
            flash('Usuario actualizado con éxito.', 'success')
            return jsonify({'status': 'success', 'message': 'Usuario actualizado con éxito.', 'redirect': url_for('configuraciones.administracion_de_usuarios')})
        else:
            flash('Error al actualizar el usuario.', 'error')
            return jsonify({'status': 'error', 'message': 'Error al actualizar el usuario.', 'redirect': url_for('configuraciones.administracion_de_usuarios')}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'redirect': url_for('configuraciones.administracion_de_usuarios')}), 500


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


# ------------------------- SUPPLIER ROUTES ------------------------- #
@configuraciones_blueprint.route('/suppliers_management')
@requires_roles('desarrollador')
def suppliers_management() -> str:
    form = SupplierForm()
    try:
        data: List[Dict] = Supplier.get_all()
        data = format_suppliers_data_for_render(data)
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
def create_supplier() -> str:
    form = SupplierForm()
    try:
        if form.validate_on_submit():
            rut, business_name, trading_name, credit_term, delivery_period = format_supplier_data_for_database(form)
            Supplier.create(rut=rut, 
                            business_name=business_name,
                            trading_name=trading_name,
                            credit_term=credit_term,
                            delivery_period=delivery_period)
            flash('Proveedor añadido con éxito', 'success')
        else:
            # Form validation failed
            errors = {field.name: field.errors for field in form if field.errors}
            flash(
                f'ERROR 400 (BAD REQUEST): '
                f'{", ".join([f"{errors[key]}" for key in errors.keys()])}',
                'error',
            )
    except Exception as ex:
        flash(F'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('configuraciones.suppliers_management'))

@configuraciones_blueprint.route('/edit_supplier/<int:supplier_id>', methods=['POST'])
@requires_roles('desarrollador')
def edit_supplier(supplier_id: int) -> str:
    form = SupplierForm()
    form.id.data = supplier_id
    try:
        if form.validate_on_submit():
            rut, business_name, trading_name, credit_term, delivery_period = format_supplier_data_for_database(form)
            Supplier.edit(supplier_id, 
                          rut=rut, 
                          business_name=business_name,
                          trading_name=trading_name,
                          credit_term=credit_term,
                          delivery_period=delivery_period)
            flash('Cambios guardados con éxito', 'success')
        else:
            # Form validation failed
            errors = {field.name: field.errors for field in form if field.errors}
            flash(
                f'ERROR 400 (BAD REQUEST): '
                f'{", ".join([f"{errors[key]}" for key in errors.keys()])}',
                'error',
            )
    except Exception as ex:
        flash(F'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally: 
        return redirect(url_for('configuraciones.suppliers_management'))

@configuraciones_blueprint.route('/delete_supplier/<int:supplier_id>')
@requires_roles('desarrollador')
def delete_supplier(supplier_id: int) -> Response:
    try:
        Supplier.delete(supplier_id)
        flash('Proveedor eliminado con éxito', 'success')
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('configuraciones.suppliers_management'))
    
@configuraciones_blueprint.route('/exportar_proveedores')
@requires_roles('desarrollador')
def export_suppliers():
    try:
        suppliers_data: List[Dict] = Supplier.get_all()
        suppliers_data = format_suppliers_data_for_render(suppliers_data)

        column_order = ['rut', 'business_name', 'trading_name', 'credit_term', 'delivery_period']
        df = pd.DataFrame(suppliers_data).reindex(columns=column_order)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Proveedores')

        output.seek(0)

        return send_file(output, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', download_name='proveedores.xlsx')
    
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
        return redirect(url_for('configuraciones.suppliers_management'))

@configuraciones_blueprint.route('/importar_proveedores', methods=['POST'])
@requires_roles('desarrollador')
def import_suppliers():
    try:
        required_columns = ['rut', 'business_name', 'trading_name', 'credit_term', 'delivery_period']
        file = request.files['file']
        if file.filename.endswith('.xlsx') or file.filename.endswith('xls'):
            df = pd.read_excel(file)
            if not all(column in df.columns for column in required_columns):
                flash('El archivo Excel no tiene todas las columnas requeridas', 'error')
                return redirect(url_for('configuraciones.suppliers_management'))
            
            if df[required_columns].isnull().any().any():
                # df.dropna(subset=required_columns, inplace=True)
                flash('Todos los datos deben estar llenos en el archivo Excel', 'error')
                return redirect(url_for('configuraciones.suppliers_management'))

            suppliers_data = df.to_dict(orient='records')

            for supplier in suppliers_data:
                supplier['rut'] = format_rut(supplier['rut'])
                supplier['credit_term'] = CreditTerm(supplier['credit_term'])

            new_df = pd.DataFrame(suppliers_data)

            Supplier.create_from_df(new_df)

            flash('Proveedores importados con éxito', 'success')
        else:
            flash('ERROR 400 (BAD REQUEST): El archivo debe estar en formato .xlsx', 'error')
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('configuraciones.suppliers_management'))