from __future__ import annotations
from datetime import time
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, Field, HiddenField, IntegerField
from wtforms_components import DateField, TimeField, TimeRange
from wtforms.validators import DataRequired, Length, ValidationError
from decorators.roles import requires_roles
from datetime import datetime, timedelta
from models.employee import Employee
from models.model_user import ModelUser
from models.overtime_hours import OvertimeRecord
from rut_chile import rut_chile
from typing import List, Dict, Tuple

START_YEAR: int = 2020
START_MONTH: int = 1

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 
         'Mayo', 'Junio', 'Julio', 'Agosto',
         'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

human_resources_blueprint = Blueprint('human_resources', __name__)
            
def format_run(run: str) -> str:        
    run = run.replace('.', '').replace('-', '')  # Remove existing formatting
    body, verifier = run[:-1], run[-1]  # Split into body and verifier
    formatted_body = '.'.join([body[max(i-3, 0):i] for i in range(len(body), 0, -3)][::-1])
    return f"{formatted_body}-{verifier}"

def format_employee_data_for_database(form: EmployeeForm) -> Tuple:
    run = format_run(form.run.data)
    first_name = form.first_name.data.capitalize()
    last_name = form.last_name.data.capitalize()
    joined_in = form.joined_in.data
    lunch_break = form.lunch_break.data
    user_id = form.user_id.data
    return run, first_name, last_name, joined_in, lunch_break, user_id

def format_employees_data_for_render(employees_data: List[Dict | None], 
                                     form: EmployeeForm) -> List[Dict | None]:
    for employee in employees_data:
        employee['username']: str = [
            user[1] 
            for user in form.user_id.choices 
            if user[0] == employee['user_id']
        ][0]
        employee['joined_in'] = employee['joined_in'].strftime('%d.%m.%Y')
        employee['lunch_break'] = employee['lunch_break'].strftime('%H:%M')
        
    return employees_data

def format_overtime_record_data_for_database(form: OvertimeRecordForm) -> Tuple:
    employee_id = form.employee_id.data
    month = form.month.data
    overtime_hours = form.overtime_hours.data
    return employee_id, month, overtime_hours

def get_month_list(start_year: int, start_month: int) -> List[str]:
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime.now()
    months = []

    while start_date <= end_date:
        months.append(start_date.strftime("%m.%Y"))
        # Move to the next month
        start_date += timedelta(days=32)
        start_date = start_date.replace(day=1)

    return months
    
# Función para generar las opciones de años
def get_years() -> List[Tuple[str]]:
    current_year = datetime.now().year
    return [(str(year), str(year)) for year in range(current_year, current_year - 10, -1)]

# Función para generar las opciones de días (del 1 al 31)
dias = [(str(day).zfill(2), str(day).zfill(2)) for day in range(1, 32)]

class RUNValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if not rut_chile.is_valid_rut(field.data):
            raise ValidationError("Invalid RUN.")
          
class NoRUNDuplicateValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        for employee in Employee.get_all():
            if format_run(field.data) == employee['run'] and form.id.data != employee['id']:
                raise ValidationError("There is already an employee with this RUN.")

class EmployeeForm(FlaskForm):
    id = HiddenField('ID de empleado')
    run = StringField('RUN (ej: 21261098-4)', 
        validators=[DataRequired(), RUNValidator(), NoRUNDuplicateValidator()]
    )
    first_name = StringField('Nombre', validators=[DataRequired()])
    last_name = StringField('Apellido', validators=[DataRequired()])
    joined_in: DateField = DateField('Fecha de Incorporación', validators=[DataRequired()])
    lunch_break = TimeField('Time', validators=[
        TimeRange(
            min=time(12, 0), 
            max=time(16, 0),
            message='Time must be between 12:00 and 16:00.'
        )
    ])
    user_id = SelectField(
        'Usuario', coerce=int, 
        choices=[(user['id'], user['username']) for user in ModelUser.get_all_users()]
    )
    
class OvertimeRecordForm(FlaskForm):
    employee_id = SelectField(
        'Empleado', coerce=int,
        choices=[
            (
                employee['id'], 
                ' '.join((employee['first_name'], employee['last_name']))
            ) 
            for employee in Employee.get_all()
        ]
    )
    month = SelectField('Mes', choices=get_month_list(START_YEAR, START_MONTH))
    overtime_hours = IntegerField('Horas Extra')
    
    
    
    
# <----- Employees' Configuration -----> #
@human_resources_blueprint.route('/employees_management')
@requires_roles('desarrollador')
def employees_management() -> str:
    form = EmployeeForm()
    try:
        # Format role data for the SelectField
        data: List[Dict] = Employee.get_all()
        data = format_employees_data_for_render(data, form)
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
    form = EmployeeForm()
    try:
        if form.validate_on_submit():
            run, first_name, last_name, joined_in, lunch_break, user_id = format_employee_data_for_database(form)
            Employee.create(
                run=run, 
                first_name=first_name, 
                last_name=last_name, 
                joined_in=joined_in, 
                lunch_break=lunch_break, 
                user_id=user_id
            )
            flash('Empleado añadido con éxito', 'success')
        else:
            # Form validation failed
            errors = {field.name: field.errors for field in form if field.errors}
            flash(
                f'ERROR 400 (BAD REQUEST): '
                f'{", ".join([f"{errors[key]}" for key in errors.keys()])}',
                'error',
            )
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error') 
    finally:
        return redirect(url_for('human_resources.employees_management')) 


@human_resources_blueprint.route('/edit_employee/<int:employee_id>', methods=['POST'])
@requires_roles('desarrollador')
def edit_employee(employee_id: int) -> str:
    form = EmployeeForm()
    form.id.data = employee_id
    try:
        if form.validate_on_submit():
            run, first_name, last_name, joined_in, lunch_break, user_id = format_employee_data_for_database(form)
            Employee.edit(employee_id,
                          run=run, 
                          first_name=first_name,
                          last_name=last_name,
                          joined_in=joined_in,
                          lunch_break=lunch_break,
                          user_id=user_id)
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
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error') 
    finally:
        return redirect(url_for('human_resources.employees_management'))       
   
    
@human_resources_blueprint.route('/delete_employee/<int:employee_id>')
@requires_roles('desarrollador')
def delete_employee(employee_id: int) -> Response:
    try:
        Employee.delete(employee_id)
        flash('Empleado eliminado con éxito', 'success')
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('human_resources.employees_management'))
    
    


# <----- Overtime Record' Configuration -----> #
@human_resources_blueprint.route('/overtime_hours_management')
@requires_roles('desarrollador')
def overtime_hours_management() -> str:
    form = OvertimeRecordForm()
    try:
        # Format role data for the SelectField
        data: List[Dict] = OvertimeRecord.get_all()
        # data = format_employees_data_for_render(data, form)
        return render_template('human_resources/overtime_hours_management/overtime_hours_management.html', 
                               page_title="Registro de Horas Extra", 
                               data=data,
                               form=form)  
    except Exception as e:
        return render_template('error.html'), 500

  
@human_resources_blueprint.route('/create_overtime_record', methods=['POST'])
@requires_roles('desarrollador')
def create_overtime_record() -> str:
    form = OvertimeRecordForm()
    try:
        if form.validate_on_submit():
            employee_id, month, overtime_hours = format_overtime_record_data_for_database(form)
            OvertimeRecord.create(employee_id=employee_id, month=month, overtime_hours=overtime_hours)
            flash('Registro añadido con éxito', 'success')
        else:
            # Form validation failed
            errors = {field.name: field.errors for field in form if field.errors}
            flash(
                f'ERROR 400 (BAD REQUEST): '
                f'{", ".join([f"{errors[key]}" for key in errors.keys()])}',
                'error',
            )
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error') 
    finally:
        return redirect(url_for('human_resources.employees_management')) 


@human_resources_blueprint.route('/edit_overtime_record/<int:employee_id>/<string:month>', methods=['POST'])
@requires_roles('desarrollador')
def edit_overtime_record(employee_id: int, month: str) -> str:
    form = OvertimeRecordForm()
    try:
        if form.validate_on_submit():
            employee_id, month, overtime_hours = format_overtime_record_data_for_database(form)
            OvertimeRecord.edit(employee_id, month, overtime_hours=overtime_hours)
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
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error') 
    finally:
        return redirect(url_for('human_resources.employees_management'))       


@human_resources_blueprint.route('/delete_employee/<int:employee_id>/<string:month>')
@requires_roles('desarrollador')
def delete_overtime_record(employee_id: int, month) -> str:
    try:
        OvertimeRecord.delete(employee_id)
        flash('Empleado eliminado con éxito', 'success')
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('human_resources.employees_management')) 
    

"""
@human_resources_blueprint.route('/get_overtime_record/<int:employee_id>/<string:month>')
@requires_roles('desarrollador')
def get_overtime_record(employee_id: int, month: str) -> Response:
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
"""