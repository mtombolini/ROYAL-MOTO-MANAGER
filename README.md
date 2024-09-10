
### Descripción de Carpetas y Archivos Principales

- **api/**: Contiene extractores de datos que se encargan de obtener información de diversas fuentes y procesarla.
- **app/**: Contiene la lógica principal de la aplicación, incluyendo la configuración, inicialización de la base de datos y el servidor Flask.
- **backup/**: Archivos de respaldo de la base de datos y otros datos importantes.
- **bin/**: Scripts ejecutables para tareas específicas, como el manejo de versiones con Git.
- **databases/**: Archivos relacionados con la gestión de la base de datos.
- **decorators/**: Decoradores utilizados en la aplicación para manejar roles y permisos.
- **extras/**: Funciones y scripts adicionales que no encajan en otras categorías.
- **logs/**: Archivos de registro para monitorear y depurar la aplicación.
- **models/**: Definiciones de modelos de datos utilizando SQLAlchemy.
- **routes/**: Definiciones de rutas de la aplicación Flask.
- **services/**: Servicios y lógica de negocio, incluyendo análisis de datos y gestión de inventarios.
- **static/**: Archivos estáticos como CSS, JavaScript e imágenes.
- **templates/**: Plantillas HTML para la interfaz de usuario.
- **venv/**: Entorno virtual de Python.

### Archivos Clave

- **parameters.py**: Parámetros de configuración globales.
- **requirements.txt**: Lista de dependencias del proyecto.
- **.gitignore**: Archivos y carpetas que deben ser ignorados por Git.

## Instalación

1. Clona el repositorio:
    ```sh
    git clone <URL_DEL_REPOSITORIO>
    ```
2. Navega al directorio del proyecto:
    ```sh
    cd <NOMBRE_DEL_PROYECTO>
    ```
3. Crea y activa un entorno virtual:
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```
4. Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

## Uso

1. Inicializa la base de datos:
    ```sh
    python -m app.init_db
    ```
2. Ejecuta la aplicación:
    ```sh
    python -m app.app
    ```

La aplicación estará disponible en `http://localhost:8000`.

## Módulos Principales

### [`api/`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fapi%2F%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/api/")

Contiene extractores de datos que obtienen y procesan información de diversas fuentes. Ejemplo: [`api/extractors/document_extractor.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fapi%2Fextractors%2Fdocument_extractor.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/api/extractors/document_extractor.py").

### [`app/`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fapp%2F%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/app/")

Contiene la lógica principal de la aplicación, incluyendo la configuración y el servidor Flask. Ejemplo: [`app/api_main.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fapp%2Fapi_main.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/app/api_main.py").

### [`models/`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fmodels%2F%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/models/")

Define los modelos de datos utilizando SQLAlchemy. Ejemplo: [`models/productos.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fmodels%2Fproductos.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/models/productos.py").

### [`routes/`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Froutes%2F%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/routes/")

Define las rutas de la aplicación Flask. Ejemplo: [`routes/api_routes.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Froutes%2Fapi_routes.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/routes/api_routes.py").

### [`services/`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fservices%2F%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/services/")

Contiene servicios y lógica de negocio, como análisis de datos y gestión de inventarios. Ejemplo: [`services/analysis/buys_analisys.py`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2Fhome%2Ffranco-anfossi%2FDocumentos%2FPersonal%2FCoding%2FROYAL-MOTO-MANAGER%2Fservices%2Fanalysis%2Fbuys_analisys.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/home/franco-anfossi/Documentos/Personal/Coding/ROYAL-MOTO-MANAGER/services/analysis/buys_analisys.py").

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.