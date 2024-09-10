## APP

Esta carpeta contiene los archivos principales de la aplicación, incluyendo la configuración, la inicialización de la base de datos, la interfaz de la API y la lógica principal de extracción y análisis de datos.

### api_main.py

Este archivo define la clase `ApiMain`, que es responsable de orquestar la extracción de datos de diferentes fuentes utilizando las clases `Extractor` definidas en la carpeta `api/extractors`. 

**Descripción:**

1. **Inicialización de extractores:** Se inicializan instancias de cada extractor (Ventas, Oficina, Producto, Devoluciones, Documento, Envío, Recepción, Lista de Precios, Consumo) con un token de acceso.
2. **Bucle principal:** El método `main` ejecuta un bucle infinito que realiza las siguientes acciones:
    * **Ejecución de extractores:** Se llama al método `run` de cada extractor, pasándole una instancia de `DataFrameMain` para almacenar los datos extraídos.
    * **Creación de la base de datos:** Una vez que todos los extractores han terminado, se crea una sesión de base de datos y se llama al método `create_data_base` de `DataFrameMain` para guardar los datos extraídos en la base de datos.
    * **Pausa y reinicio:** Se espera 10 segundos antes de reiniciar el ciclo.
3. **Manejo de errores:** Se manejan las excepciones que puedan ocurrir durante la ejecución y se imprime un mensaje de error.
4. **Salida del programa:** Al finalizar el bucle, se imprime un mensaje de limpieza y salida.

**Uso:**

Este archivo se ejecuta como un script independiente para iniciar el proceso de extracción y almacenamiento de datos. (ver `extraction_main.py`)

### app.py

Este archivo define la aplicación Flask principal y configura las rutas, el manejo de sesiones y el manejo de errores.

**Descripción:**

1. **Inicialización de la aplicación:** Se crea una instancia de la aplicación Flask y se configura con la clase `Config` definida en `config.py`.
2. **Registro de blueprints:** Se registran los blueprints que definen las diferentes rutas de la aplicación (autenticación, página principal, tablas, compras, reportes, configuraciones, recursos humanos, rutas de la API).
3. **Manejo de sesiones:** Se configura Flask-Login para manejar las sesiones de usuario.
4. **Manejo de errores:** Se definen funciones para manejar los errores 401 (no autorizado) y 404 (no encontrado).

**Uso:**

Este archivo se ejecuta como un script independiente para iniciar el servidor web de la aplicación.

### config.py

Este archivo define la clase `Config`, que contiene la configuración de la aplicación, como la clave secreta, la URL de la base de datos y el tipo de configuración (desarrollo, producción, etc.).

**Descripción:**

1. **Carga de variables de entorno:** Se utiliza `dotenv` para cargar las variables de entorno desde el archivo `.env`.
2. **Definición de la clase `Config`:** Se definen las variables de configuración como atributos de la clase `Config`.

**Uso:**

La clase `Config` se utiliza para configurar la aplicación Flask en `app.py`.

### dataframe_main.py

Este archivo define la clase `DataFrameMain`, que es responsable de almacenar y procesar los datos extraídos por las clases `Extractor`. 

**Descripción:**

1. **Atributos:** Define atributos para almacenar los DataFrames de cada entidad (productos, stocks, consumos, ventas, documentos, recepciones, devoluciones, lista de precios, proveedores, envíos, oficinas).
2. **Métodos de corrección:** Define métodos para limpiar y corregir los datos de cada DataFrame, como eliminar filas con valores faltantes o filtrar filas según criterios específicos.
3. **Métodos de creación:** Define métodos para crear instancias de las clases de modelo (Producto, Stock, Consumo, etc.) a partir de los datos de los DataFrames y guardarlas en la base de datos.

**Uso:**

La clase `DataFrameMain` se utiliza en `api_main.py` para almacenar los datos extraídos por los extractores y luego crear la base de datos a partir de estos datos.

### extraction_main.py

Este archivo define la clase `ExtractionMain`, que es responsable de ejecutar la extracción de datos, el cálculo del último costo neto y el análisis de datos.

**Descripción:**

1. **Método `run_extraction`:** 
    * Ejecuta la extracción de datos llamando al método `main` de `ApiMain`.
    * Calcula el último costo neto llamando al método `main_extraction` de `LastNetCostExtractor`.
    * Inicializa la activación del producto llamando a la función `init_product_activation`.
    * Realiza el análisis de datos creando una sesión de base de datos y llamando al método `main` de `Analyser`.

**Uso:**

Este archivo se ejecuta como un script independiente para iniciar el proceso completo de extracción, cálculo del último costo neto, inicialización de la activación del producto y análisis de datos. (Utilizar este archivo para obtencion de datos y calculo de stock)

### init_db.py

Este archivo define la clase `InitDB`, que es responsable de crear la base de datos e inicializarla con datos iniciales, como roles de usuario y un usuario administrador.

**Descripción:**

1. **Método `create_data_base`:** Crea las tablas en la base de datos utilizando SQLAlchemy.
2. **Método `initialize_database`:** Inicializa la base de datos con roles de usuario y un usuario administrador si aún no existen.
3. **Método `create_roles`:** Crea los roles de usuario (superadministrador, desarrollador, administrador, invitado).
4. **Método `create_superadmin`:** Crea un usuario superadministrador con nombre de usuario "superadmin" y contraseña "admin".

**Uso:**

Este archivo se ejecuta como un script independiente para crear e inicializar la base de datos. Utilizar este archivo siempre y cuando las tablas no existan en la base de datos. (construye parcial y completamente la base de datos)