from __future__ import annotations
from parameters import FORM_DATE_FORMAT, SCHEDULE_RECORDS_DATE_FORMAT, SCHEDULE_RECORDS_TIME_FORMAT, FORM_COMPLETE_DATE_FORMAT
from datetime import time
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, Field, HiddenField, IntegerField
from wtforms_components import DateField, TimeField, TimeRange
from wtforms.validators import DataRequired, Length, ValidationError
from decorators.roles import requires_roles
from datetime import datetime, timedelta, date
from models.employee import Employee
from models.model_user import ModelUser
from models.overtime_hours import (OvertimeRecord,
    OvertimeRecordRecordNotFoundError, OvertimeRecordKeyError,
    OvertimeRecordRecordColumnNotFoundError,
)                             
from rut_chile import rut_chile
from typing import List, Dict, Tuple
from math import ceil

START_YEAR: int = 2020
START_MONTH: int = 1

WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 
         'Mayo', 'Junio', 'Julio', 'Agosto',
         'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

human_resources_blueprint = Blueprint('human_resources', __name__)

def reformat_strftime(strf_date: str, from_format: str, to_format: str) -> str:
    parsed_date = datetime.strptime(strf_date, from_format)
    reformated_date = parsed_date.strftime(to_format)
    return reformated_date
    
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

def format_overtime_record_time_attr_value_for_database(value: str) -> time:
    return datetime.strptime(value, SCHEDULE_RECORDS_TIME_FORMAT).time()

def format_timedelta_for_render(value: timedelta) -> str:
    total_seconds = int(value.total_seconds())
    if total_seconds != 0:
        hours = abs(total_seconds) // 3600 * int(total_seconds / abs(total_seconds))
        minutes = (abs(total_seconds) % 3600) // 60
        seconds = abs(total_seconds) % 60
    else:
        hours, minutes, seconds = (0,) * 3
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"

def format_overtime_record_data_for_render(data: List[Dict], 
                                           weekly_data: List[Dict[str, int | timedelta]], 
                                           summary_data: Dict) -> Tuple(List[Dict], Dict):
    for record in data:
        record['date'] = record['date'].strftime(FORM_COMPLETE_DATE_FORMAT)
        record['total_hours_worked'] = format_timedelta_for_render(record['total_hours_worked']) if record['total_hours_worked'] is not None else None
        record['overtime_hours'] = format_timedelta_for_render(record['overtime_hours']) if record['overtime_hours'] is not None else None
        
    for week in weekly_data:
        for key, value in week.items():
            if not isinstance(value, int):
                if isinstance(value, date):
                    week[key] = week[key].strftime(FORM_COMPLETE_DATE_FORMAT)
                else:
                    week[key] = format_timedelta_for_render(week[key])
            
    for key in summary_data.keys():
        summary_data[key] = format_timedelta_for_render(summary_data[key])
        
    return data, weekly_data, summary_data

def get_month_list(start_year: int, start_month: int) -> List[str]:
    start_date = datetime(start_year, start_month, 1)
    end_date = datetime.now()
    months = []

    while start_date <= end_date:
        months.append(start_date.strftime(FORM_DATE_FORMAT))
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
    
    


# <----- Overtime Records' Configuration -----> #
@human_resources_blueprint.route('/overtime_hours_management/<int:employee_id>/<string:month>')
@requires_roles('desarrollador')
def overtime_hours_management(employee_id: int | None=None, month: str | None=None) -> str:
    form = OvertimeRecordForm()
    try:
        month = reformat_strftime(month, FORM_DATE_FORMAT, SCHEDULE_RECORDS_DATE_FORMAT)
        data, weekly_data, summary_data = OvertimeRecord.get_employee_month_schedule_record(employee_id, month) if employee_id and month else (None, None, None)
        data, weekly_data, summary_data = format_overtime_record_data_for_render(data, weekly_data, summary_data) if data and summary_data else (None, None, None)
        return render_template('human_resources/overtime_hours_management/overtime_hours_management.html', 
                               page_title="Registro de Horas Extra", 
                               month=month,
                               data=data,
                               weekly_data=weekly_data,
                               summary_data=summary_data,
                               form=form,
                               show_table=bool(employee_id) and bool(month))  
    except Exception as e:
        return render_template('error.html'), 500


@human_resources_blueprint.route('/update_overtime_record/<int:employee_id>/<string:date>', methods=['POST'])
@requires_roles('desarrollador')
def update_overtime_record(employee_id: int, date: str) -> str:
    try:
        updates = request.form
        if not updates or len(updates) != 1:
            raise AttributeError('Invalid update data')
        key, value = next(iter(updates.items()))
        valid_keys = ["check_in", "check_out", "lunch_break_start", "lunch_break_end"]
        if key not in valid_keys:
            raise KeyError('Invalid attribute for update')
        value = format_overtime_record_time_attr_value_for_database(value)
        OvertimeRecord.edit(employee_id=employee_id, date=date, **{key: value})
        flash('Registro editado exitosamente', 'success')
    except OvertimeRecordRecordColumnNotFoundError as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    except OvertimeRecordKeyError as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    except OvertimeRecordRecordNotFoundError as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')        
    except Exception as ex:
        flash(
            f'ERROR 400 (BAD REQUEST): '
            f'{str(ex)}',
            'error',
        )
    finally:
        month = "-".join(date.split("-")[:-1])
        return redirect(url_for('human_resources.overtime_hours_management', employee_id=employee_id, month=month))

@human_resources_blueprint.route('/delete_overtime_record/<int:employee_id>/<string:month>')
@requires_roles('desarrollador')
def delete_overtime_record(employee_id: int, month: str) -> str:
    try:
        OvertimeRecord.delete(employee_id, month)
        flash('Registro eliminado con éxito', 'success')
    except Exception as ex:
        flash(f'ERROR 500 (INTERNAL SERVER ERROR): {str(ex)}', 'error')
    finally:
        return redirect(url_for('human_resources.overtime_hours_management')) 
    

# <---- Asignación de Feriado ---->
@human_resources_blueprint.route('/assign_holiday/<int:employee_id>/<string:date>/<string:month>', methods=['POST'])
@requires_roles('desarrollador')
def assign_holiday_day(employee_id: int, date: str, month: str) -> str:
    flash(f'Asignaste al empleado {employee_id} en el día {date} como feriado', 'success')
    OvertimeRecord.toggle_is_holiday_status(employee_id, date)
    month = reformat_strftime(month, SCHEDULE_RECORDS_DATE_FORMAT, FORM_DATE_FORMAT)
    return redirect(url_for('human_resources.overtime_hours_management', employee_id=employee_id, month=month))


@human_resources_blueprint.route('/mark_as_vacation/<int:employee_id>/<string:date>/<string:month>', methods=['POST'])
@requires_roles('desarrollador')
def mark_as_vacation(employee_id: int, date: str, month: str) -> str:
    flash(f'Asignaste al empleado {employee_id} en el día {date} como vacaciones pagadas.', 'success')
    OvertimeRecord.toggle_is_on_vacation_status(employee_id, date)
    month = reformat_strftime(month, SCHEDULE_RECORDS_DATE_FORMAT, FORM_DATE_FORMAT)
    return redirect(url_for('human_resources.overtime_hours_management', employee_id=employee_id, month=month))


@human_resources_blueprint.route('/mark_as_absence/<int:employee_id>/<string:date>/<string:month>', methods=['POST'])
@requires_roles('desarrollador')
def mark_as_absence(employee_id: int, date: str, month: str) -> str:
    flash(f'Asignaste al empleado {employee_id} en el día {date} como ausencia (Permiso no pagado).', 'success')
    OvertimeRecord.toggle_absence_status(employee_id, date)
    month = reformat_strftime(month, SCHEDULE_RECORDS_DATE_FORMAT, FORM_DATE_FORMAT)
    return redirect(url_for('human_resources.overtime_hours_management', employee_id=employee_id, month=month))
