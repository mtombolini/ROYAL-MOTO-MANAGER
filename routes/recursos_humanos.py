from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms_components import DateField
from wtforms.validators import DataRequired, Length
from decorators.roles import requires_roles
from datetime import datetime
from models.model_employe import ModelEmployee
from models.model_user import ModelUser

recursos_humanos_blueprint = Blueprint('recursos_humanos', __name__)

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
opciones_horario_colacion = [
    (1, 'Opción 1'),
    (2, 'Opción 2'),
    (3, 'Opción 3'),
    # Agrega más opciones según tus necesidades
]

class NewEmployeeForm(FlaskForm):
    rut = StringField('Rut (ej: 21261098-4)', validators=[DataRequired(), Length(min=10, max=10)])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    fecha_incorporacion = DateField('Fecha de Incorporación', validators=[DataRequired()])
    horario_colacion = SelectField('Horario Colación', coerce=int, choices=opciones_horario_colacion, validators=[DataRequired()])
    user_id = SelectField('Usuario', coerce=int, choices=[])

@recursos_humanos_blueprint.route('/employees_administration')
@requires_roles('desarrollador')
def employees_administration():
    form = NewEmployeeForm()
    users_info = ModelUser.get_all_users()
    form.user_id.choices = [(user['id'], user['username']) for user in users_info]
    try:
        data = ModelEmployee.get_all_employees()
        return render_template('recursos_humanos/employees/view_employees.html', form=form, page_title="Administración de Empleados", data=data)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500


@recursos_humanos_blueprint.route('/create_employee', methods=['POST'])
@requires_roles('desarrollador')
def create_employee():
    form = NewEmployeeForm(request.form)
    users_info = ModelUser.get_all_users()
    form.user_id.choices = [(user['id'], user['username']) for user in users_info]
    if form.validate_on_submit():
        user_id = form.user_id.data
        rut = form.rut.data
        nombre = form.nombre.data
        apellido = form.apellido.data
        fecha_incorporacion = form.fecha_incorporacion.data
        horario_colacion = form.horario_colacion.data

        try:
            new_employee = ModelEmployee.create(user_id, rut, nombre, apellido, fecha_incorporacion, horario_colacion)
            flash('Empleado registrado con éxito', 'success')
        except Exception as e:
            flash(f'Error al crear empleado: {e}', 'error')

        return redirect(url_for('recursos_humanos.employees_administration'))
    else:
        flash('Error en el formulario', 'danger')
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"Error en {fieldName}: {err}", 'danger')
        return redirect(url_for('recursos_humanos.employees_administration'))
