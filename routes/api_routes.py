import os
import time
import json
import subprocess

from threading import Thread
from decorators.roles import requires_roles
from app.flags import stop, clear_stop_signal, stop_signal_is_set
from flask import Blueprint, current_app, flash, render_template, jsonify

api_blueprint = Blueprint('api_call', __name__)
api_actualizacion = Blueprint('api_actualizacion', __name__)
active_threads = []

def run_api_module(app):
    with app.app_context():
        project_root = os.path.dirname(current_app.root_path)
        module_path = 'app.extraction_main'
        python_executable = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')
        if not os.path.exists(python_executable):
            python_executable = 'python'

        clear_stop_signal()

        try:
            while not stop_signal_is_set():
                result = subprocess.run([python_executable, '-m', module_path], capture_output=True, text=True, cwd=project_root)
                if result.returncode == 0:
                    flash('La información de la API se obtuvo con éxito.', 'success')
                else:
                    flash(f'Hubo un error al obtener la información de la API: {result.stderr}', 'error')

                time.sleep(1)
        except Exception as e:
            flash(f'Ocurrió un error inesperado: {str(e)}', 'error')

@api_blueprint.route('/run_api_calls')
@requires_roles()
def run_api_calls():
    global active_threads

    stop()

    if any(thread.is_alive() for thread in active_threads):
        time.sleep(10)

    active_threads = [t for t in active_threads if t.is_alive()]

    with open('logs/api_status.log', 'w') as log_file:
        log_file.write('')

    clear_stop_signal()

    thread = Thread(target=run_api_module, args=(current_app._get_current_object(),))
    active_threads.append(thread)
    thread.start()

    return render_template('api/espera.html', page_title="Solicitud de actualización manual API")


@api_actualizacion.route('/actualizar_estado')
def actualizar_estado():
    estados = []
    try:
        with open('logs/api_status.log', 'r') as file:
            for line in file:
                try:
                    estado = json.loads(line)
                    estados.append(estado)
                except json.JSONDecodeError:
                    continue
                
    except FileNotFoundError:
        estados = [{"tipo": "error", "mensaje": "Archivo de log no encontrado."}]
    return jsonify(estados)