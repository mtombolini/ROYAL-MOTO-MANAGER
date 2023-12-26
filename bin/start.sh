#!/bin/bash

# Inicializa la base de datos
python -m app.init_db

# Inicia la aplicación web
gunicorn app.app:app
