from flask import Blueprint, current_app, redirect, url_for, flash
import subprocess
import os

api_blueprint = Blueprint('api_call', __name__)

@api_blueprint.route('/run_api_calls')
def run_api_calls():
    project_root = os.path.dirname(current_app.root_path)

    module_path = 'app.api_main'

    python_executable = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(python_executable):
        python_executable = 'python'

    result = subprocess.run([python_executable, '-m', module_path], capture_output=True, text=True, cwd=project_root)
    if result.returncode == 0:
        flash('La información de la API se obtuvo con éxito.', 'success')
    else:
        flash(f'Hubo un error al obtener la información de la API: {result.stderr}', 'error')
    
    return redirect(url_for('home.home'))