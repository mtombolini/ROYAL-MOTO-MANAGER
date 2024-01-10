from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms_components import DateField
from wtforms.validators import DataRequired, Length
from decorators.roles import requires_roles
from datetime import datetime
from models.model_employe import ModelEmployee

recursos_humanos_blueprint = Blueprint('recursos_humanos', __name__)

# -------------------------------------------------------------------------------------------------- #

# Define una función para generar las opciones de años
def get_years():
    current_year = datetime.now().year
    return [(str(year), str(year)) for year in range(current_year, current_year - 10, -1)]

# Define una lista de opciones para el mes
meses = [('01', 'Enero'), ('02', 'Febrero'), ('03', 'Marzo'), ('04', 'Abril'),
         ('05', 'Mayo'), ('06', 'Junio'), ('07', 'Julio'), ('08', 'Agosto'),
         ('09', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]

# Define una función para generar las opciones de días (del 1 al 31)
dias = [(str(day).zfill(2), str(day).zfill(2)) for day in range(1, 32)]

# Define las opciones para el campo de horario de colación
opciones_horario_colacion = [
    (1, 'Opción 1'),
    (2, 'Opción 2'),
    (3, 'Opción 3'),
    # Agrega más opciones según tus necesidades
]

class NewEmployeeForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    rut = StringField('Rut (ej: 21261098-4)', validators=[DataRequired(), Length(min=10, max=10)])
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    
    # Campo para la fecha de incorporación utilizando DateField
    fecha_incorporacion = DateField('Fecha de Incorporación', validators=[DataRequired()])
    
    # Campo para el horario de colación
    horario_colacion = SelectField('Horario Colación', coerce=int, choices=opciones_horario_colacion, validators=[DataRequired()])

    
@recursos_humanos_blueprint.route('/employees_administration')
@requires_roles('desarrollador')
def employees_administration():
    form = NewEmployeeForm()
    try:
        data = ModelEmployee.get_all_employees()
        return render_template('recursos_humanos/employees/view_employees.html', form=form, page_title="Administración de Empleados", data=data)
    except Exception as e:
        print(e)
        return render_template('error.html'), 500
    
    
@recursos_humanos_blueprint.route('/employees_registration')
@requires_roles('desarrollador')
def employees_registration():
    form = NewEmployeeForm(request.form)
    if form.validate_on_submit():

        # Aquí puedes procesar el formulario y guardar los datos en la base de datos
        # Puedes acceder a los datos del formulario a través de form.username.data, form.rut.data, etc.
        # Implementa la lógica para guardar los datos en la base de datos
        flash('Empleado registrado con éxito', 'success')
        print(request.form)
        return redirect(url_for('recursos_humanos.employees_administration'))
    else:
        flash('Error en el formulario', 'danger')
        return render_template('recursos_humanos/employees/view_employees.html', form=form, page_title="Administración de Empleados")
    
@recursos_humanos_blueprint.route('/create_employee', methods=['POST'])
@requires_roles('desarrollador')
def create_employee():
    form = NewEmployeeForm(request.form)
    username = form.username
    rut = form.rut
    nombre = form.nombre
    apellido = form.apellido
    
    if form.validate_on_submit():
        description = form.description.data
        new_employee, session = ModelEmployee.create(username, rut, nombre, apellido, fecha_incorporacion, horario_colacion)
        session.close()

        if new_role is None:
            flash('El rol ya existe o hubo un error en el registro.', 'error')
        else:
            flash('Rol creado exitosamente.', 'success')

        return redirect(url_for('configuraciones.administracion_de_roles'))
