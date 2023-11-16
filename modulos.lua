project_name/
|-- env/                 # Entorno virtual
|-- src/                 # Carpeta principal del código fuente
|   |-- app.py           # Archivo principal de la aplicación
|   |-- config.py        # Configuraciones
|
|   |-- api/
|   |   |-- bsale.py
|
|   |-- models/
|   |   |-- __init__.py
|   |   |-- ModelUser.py
|   |   |-- entities/
|   |       |-- __init__.py
|   |       |-- User.py
|
|   |-- services/        # (Opcional) Funcionalidades de procesamiento de datos y otros servicios
|
|   |-- decorators/      # Carpeta para decoradores personalizados
|   |   |-- __init__.py
|   |   |-- roles.py     # Aquí se ubicaría la función requires_roles y otros decoradores relacionados
|
|   |-- routes/          # Carpeta para los Blueprints
|   |   |-- __init__.py
|   |   |-- auth.py      # Rutas relacionadas con la autenticación
|   |   |-- home.py      # Rutas relacionadas con la página de inicio y otras funcionalidades
|
|   |-- static/
|   |   |-- css/
|   |   |-- img/
|
|   |-- templates/
|   |   |-- auth/
|   |   |   |-- login.html
|   |   |-- header.html
|   |   |-- home.html
|   |   |-- stock_critio.html
|   |   |-- layout.html
|   |   |-- alerta_permisos_usuarios.html
|
|   |-- test/
|   |   |-- api/
|   |   |-- other/
|
|-- .gitignore
|-- README.md
|-- requirements.txt
