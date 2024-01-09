from flask import Blueprint, current_app, flash, render_template, jsonify
from threading import Thread
import time
import subprocess
import os
from app.flags import stop, clear_stop_signal, stop_signal_is_set
import json

api_blueprint = Blueprint('api_call', __name__)
api_actualizacion = Blueprint('api_actualizacion', __name__)
active_threads = []

def run_api_module(app):
    # Crea un contexto de aplicación
    with app.app_context():
        project_root = os.path.dirname(current_app.root_path)
        module_path = 'app.api_main'
        python_executable = os.path.join(project_root, 'venv', 'Scripts', 'python.exe')
        if not os.path.exists(python_executable):
            python_executable = 'python'

        # Antes de ejecutar el subproceso, asegúrate de limpiar el archivo de señal
        clear_stop_signal()

        try:
            while not stop_signal_is_set():  # <-- Aquí se aplica la condición
                result = subprocess.run([python_executable, '-m', module_path], capture_output=True, text=True, cwd=project_root)
                if result.returncode == 0:
                    flash('La información de la API se obtuvo con éxito.', 'success')
                else:
                    flash(f'Hubo un error al obtener la información de la API: {result.stderr}', 'error')

                time.sleep(1)  # Esperar un tiempo antes de volver a ejecutar
        except Exception as e:
            flash(f'Ocurrió un error inesperado: {str(e)}', 'error')

@api_blueprint.route('/run_api_calls')
def run_api_calls():
    global active_threads

    # Señalar a las threads existentes que deben detenerse
    stop()

    # Verificar si hay threads anteriores en ejecución
    if any(thread.is_alive() for thread in active_threads):
        time.sleep(10)  # Ajusta este tiempo si es necesario

    active_threads = [t for t in active_threads if t.is_alive()]

    with open('logs/api_status.log', 'w') as log_file:
        log_file.write('')

    # Limpia el archivo de señalización antes de iniciar un nuevo hilo
    clear_stop_signal()

    thread = Thread(target=run_api_module, args=(current_app._get_current_object(),))
    active_threads.append(thread)
    thread.start()

    # Redirigir a la página de espera
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
                    continue  # O manejar de alguna otra manera
        # Opcionalmente, filtra o procesa los estados según necesidad
    except FileNotFoundError:
        estados = [{"tipo": "error", "mensaje": "Archivo de log no encontrado."}]
    return jsonify(estados)