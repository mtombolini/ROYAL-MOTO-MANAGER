from flask import Blueprint, current_app, redirect, url_for, flash
import subprocess

api_blueprint = Blueprint('api_call', __name__, template_folder='../templates')

@api_blueprint.route('/run_api_calls')
def run_api_calls():
    script_path = current_app.root_path + '/api_main.py'
    
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    if result.returncode == 0:
        flash('La información de la API se obtuvo con éxito.', 'success')
    else:
        flash(f'Hubo un error al obtener la información de la API: {result.stderr}', 'error')
    
    return redirect(url_for('home.home'))