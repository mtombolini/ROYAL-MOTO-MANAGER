from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms_components import DateField
from wtforms.validators import DataRequired, Length
from decorators.roles import requires_roles
from datetime import datetime
from models.employee import Employee
from models.model_user import ModelUser
from typing import List, Dict

human_resources_blueprint = Blueprint('human_resources', __name__)

# Función para generar las opciones de años
def get_years():
    current_year = datetime.now().year
    return [(str(year), str(year)) for year in range(current_year, current_year - 10, -1)]

# Lista de opciones para el mes
meses = [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
         ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
         ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]

# Función para generar las opciones de días (del 1 al 31)
dias = [(str(day).zfill(2), str(day).zfill(2)) for day in range(1, 32)]

# Opciones para el campo de horario de colación
lunch_break_options = [
    (1, 'Opción 1'),
    (2, 'Opción 2'),
    (3, 'Opción 3'),
    # Agrega más opciones según tus necesidades
]

class NewEmployeeForm(FlaskForm):
    rut = StringField('Rut (ej: 21261098-4)', validators=[DataRequired(), Length(min=10, max=10)])
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    joined_in = DateField('Fecha de Incorporación', validators=[DataRequired()])
    lunch_break = SelectField('Horario Colación', coerce=int, choices=lunch_break_options, validators=[DataRequired()])
    user_id = SelectField('Usuario', coerce=int, choices=[])
    
# <----- Employees' Configuration -----> #
@human_resources_blueprint.route('/employees_management')
@requires_roles('desarrollador')
def employees_management() -> str:
    form = NewEmployeeForm()
    try:
        # Get the users data to populate the user_id choice field
        users_data = ModelUser.get_all_users()
        form.user_id.choices = [(user['id'], f"{user['id']} - {user['username']}") for user in users_data]
        # Format role data for the SelectField
        data: List[Dict] = Employee.get_all()
        return render_template('human_resources/employees_management/employees_management.html', 
                               page_title="Administración de Empleados", 
                               data=data,
                               form=form)  
    except Exception as e:
        return render_template('error.html'), 500


@human_resources_blueprint.route('/get_employee/<int:employee_id>')
@requires_roles('desarrollador')
def get_employee(employee_id: int) -> Response:
    try:
        employee_data: Dict = Employee.get(employee_id)
        response = jsonify(employee_data)
        response.status_code = 200 # Successful
        return response
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while fetching employee data'})
        response.status_code = 500 # Internal Server Error
        return response
    
    
@human_resources_blueprint.route('/create_employee', methods=['POST'])
@requires_roles('desarrollador')
def create_employee() -> Response:
    form = NewEmployeeForm()
    if form.validate_on_submit():
        try:
            rut = form.rut.data
            first_name = form.first_name.data
            last_name = form.last_name.data
            joined_in = form.joined_in.data
            lunch_break = form.lunch_break.data
            user_id = form.user_id.data
            
            new_employee_data: Dict = Employee.create(rut=rut, 
                                                      first_name=first_name,
                                                      last_name=last_name,
                                                      joined_in=joined_in,
                                                      lunch_break=lunch_break,
                                                      user_id=user_id)
            new_employee_data['redirect'] = 'human_resources.employees_management'
            response = jsonify(new_employee_data)
            response.status_code = 200 # Successful
            return redirect(url_for('human_resources.employees_management'))
        except Exception as ex:
            response = jsonify({'error': str(ex), 
                                'message': 'An error ocurred while creating new employee',
                                'redirect': 'human_resources.employees_management'})
            response.status_code = 500 # Internal Server Error
            return response
    else:
        # Form validation failed
        errors = {field.name: field.errors for field in form if field.errors}
        response = jsonify({'error': 'Validation failed', 
                            'message': 'Please check the form data',
                            'field errors': errors,
                            'redirect': 'human_resources.employees_management'})
        response.status_code = 400  # Bad Request (validation error)
        return response


@human_resources_blueprint.route('/edit_employee/<int:employee_id>', methods=['POST'])
@requires_roles('desarrollador')
def edit_employee(employee_id: int) -> Response:
    try:
        data = request.get_json()
        rut = data.get('rut')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        joined_in = data.get('joined_in')
        lunch_break = data.get('lunch_break')
        user_id = data.get('user_id')
        
        if None not in [rut, first_name, last_name, joined_in, lunch_break, user_id]:
            edited_employee_data: Dict = Employee.edit(rut=rut, 
                                                      first_name=first_name,
                                                      last_name=last_name,
                                                      joined_in=joined_in,
                                                      lunch_break=lunch_break,
                                                      user_id=user_id)
            response = jsonify(edited_employee_data)
            response.status_code = 200 # Successful
            return response
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while editing employee data'})
        response.status_code = 500 # Internal Server Error
        return response


@human_resources_blueprint.route('/delete_employee/<int:employee_id>')
@requires_roles('desarrollador')
def delete_employee(employee_id: int) -> Response:
    try:
        Employee.delete(employee_id)
        response = jsonify({'status': 'success', 'message': 'Proveedor eliminado con éxito.'})
        response.status_code = 200 # Successful
        return redirect(url_for('configuraciones.employees_management'))
    except Exception as ex:
        response = jsonify({'error': str(ex), 
                            'message': 'An error ocurred while deleting employee'})
        response.status_code = 500 # Internal Server Error
        return response
    