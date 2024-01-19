import os
from threading import Event

STOP_SIGNAL_FILE = 'logs/stop_signal_file.txt'
stop_flag = Event()

def stop():
    """Activa el evento y crea el archivo de señal para detener los threads."""
    stop_flag.set()
    with open(STOP_SIGNAL_FILE, 'w') as file:
        file.write('stop')

def clear_stop_signal():
    """Limpia el evento y elimina el archivo de señal si existe."""
    stop_flag.clear()
    if os.path.exists(STOP_SIGNAL_FILE):
        os.remove(STOP_SIGNAL_FILE)

def stop_signal_is_set():
    """Verifica si el evento o el archivo de señal indica que los threads deben detenerse."""
    return stop_flag.is_set() or os.path.exists(STOP_SIGNAL_FILE)