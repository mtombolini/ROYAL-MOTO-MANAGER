## RUTAS

La carpeta `/routes` contiene los archivos que definen las rutas y la lógica para las diferentes secciones de la aplicación web. Cada archivo se encarga de un conjunto específico de funcionalidades, como la autenticación, la gestión de productos, las compras, etc.

A continuación se describe cada archivo en detalle:

### api_routes.py

Este archivo define las rutas relacionadas con la API para obtener información de productos. 

**Funcionalidades:**

* **`run_api_module(app)`:** Esta función ejecuta el módulo principal de extracción de datos de la API en un subproceso separado. 
    * Utiliza `subprocess.run` para ejecutar un script Python que se encarga de la extracción.
    * Implementa un mecanismo de parada para detener la extracción cuando sea necesario.
* **`run_api_calls()`:** Define la ruta `/run_api_calls` que inicia la extracción de datos de la API.
    * Requiere el rol de "desarrollador" para acceder.
    * Detiene cualquier proceso de extracción anterior antes de iniciar uno nuevo.
* **`actualizar_estado()`:** Define la ruta `/actualizar_estado` que devuelve el estado actual de la extracción de datos.
    * Lee un archivo de registro para obtener los estados.
    * Devuelve una lista de estados en formato JSON.

**Ejemplo de uso de `subprocess.run`:**

```python
result = subprocess.run([python_executable, '-m', module_path], capture_output=True, text=True, cwd=project_root)
```

### auth.py

Este archivo gestiona las rutas relacionadas con la autenticación de usuarios, incluyendo el inicio de sesión, el registro y el cierre de sesión.

**Funcionalidades:**

* **`LoginForm` y `RegisterForm`:** Definen los formularios para el inicio de sesión y el registro, respectivamente.
* **`login()`:** Define la ruta `/login` para el inicio de sesión.
    * Valida las credenciales del usuario utilizando `ModelUser.login`.
    * Inicia la sesión del usuario con `login_user` si las credenciales son válidas.
* **`register()`:** Define la ruta `/register` para el registro de nuevos usuarios.
    * Valida la información del formulario, incluyendo la confirmación de la contraseña.
    * Registra al usuario en la base de datos utilizando `ModelUser.register`.
    * Inicia la sesión del usuario después del registro.
* **`logout()`:** Define la ruta `/logout` para el cierre de sesión.
    * Cierra la sesión del usuario con `logout_user`.

**Ejemplo de validación de formulario:**

```python
if form.validate_on_submit():
    # Procesar los datos del formulario
```

### compras.py

Este archivo gestiona las rutas relacionadas con las compras, incluyendo la gestión del carro de compras, la emisión de compras, la recepción de productos, el pago a proveedores y el análisis de rendimiento.

**Funcionalidades:**

* **`stock_critico()`:** Define la ruta `/stock_critico` que (actualmente sin funcionalidad específica).
* **`carro()`:** Define la ruta `/carro/<int:cart_id>` para mostrar el detalle de un carro de compras.
    * Obtiene la información del carro y sus detalles utilizando `ModelCart.get_cart_detail_by_id`.
    * Calcula el resumen de la compra (subtotal, impuestos, total).
* **`compras()`:** Define la ruta `/compras` que muestra la lista de carros de compras.
    * Obtiene la lista de carros utilizando `ModelCart.get_all_carts`.
* **`eliminar_carro()`:** Define la ruta `/eliminar_carro/<int:cart_id>` para eliminar un carro de compras.
    * Elimina el carro utilizando `ModelCart.delete_cart_by_id`.
* **`eliminar_producto()`:** Define la ruta `/eliminar_producto_carro/<int:cart_id>/<int:cart_detail_id>/<int:products_quantity>/<state>` para eliminar un producto de un carro de compras.
    * Elimina el detalle del carro utilizando `ModelCart.delete_cart_detail_by_id`.
    * Actualiza el carro de compras utilizando `ModelCart.check_to_update_all_cart`.
* **`agregar_producto()`:** Define la ruta `/compras` (POST) para agregar un producto al carro de compras.
    * Recibe la información del producto y la cantidad a través de una solicitud POST.
    * Crea un nuevo carro de compras si no existe uno para el proveedor del producto.
    * Crea un detalle del carro de compras con la información del producto.
    * Actualiza el monto neto y la cantidad de productos del carro.
* **`actualizar_producto_carro()`:** Define la ruta `/actualizar_producto_carro` (POST) para actualizar la cantidad y el costo de un producto en el carro de compras.
* **`emitir_compra()`:** Define la ruta `/emitir_compra` (POST) para cambiar el estado de un carro de compras a "Emitida".
* **`recepcionar_carro_compra()`:** Define la ruta `/recepcionar_carro_compra/<int:cart_id>` para mostrar la interfaz de recepción de un carro de compras.
* **`agregar_producto_recepcion()`:** Define la ruta `/agregar_producto_recepcion/<int:cart_id>` para agregar productos a un carro de compras durante la recepción.
    * Permite buscar productos por SKU en la base de datos local o a través de la API.
* **`obtener_fechas_de_pago()`:** Define la ruta `/obtener_fechas_de_pago/<int:cart_id>` (GET) para obtener las fechas de pago asociadas a un carro de compras.
* **`actualizar_fechas_de_pago()`:** Define la ruta `/actualizar_fechas_de_pago/<int:cart_id>/<state>` (POST) para actualizar las fechas de pago de un carro de compras.
* **`procesar_datos_recepcion()`:** Define la ruta `/procesar_datos_recepcion` (POST) para procesar los datos de la recepción de un carro de compras.
    * Envía los datos de recepción a la API utilizando `ReceptionPost`.
    * Actualiza el carro de compras en la base de datos local.
* **`generar_pdf()`:** Define la ruta `/generar-pdf-recepcion` (POST) para generar un PDF de la recepción de un carro de compras.
* **`rendimiento_compra()`:** Define la ruta `/rendimiento_compra/<int:cart_id>` para mostrar el análisis de rendimiento de una compra.

**Ejemplo de manejo de solicitud POST:**

```python
@compras_blueprint.route('/compras', methods=['POST'])
def agregar_producto():
    data = request.json
    # Procesar los datos de la solicitud
```

### configuraciones.py

Este archivo gestiona las rutas relacionadas con la configuración de la aplicación, incluyendo la administración de roles, usuarios y proveedores.

**Funcionalidades:**

* **Administración de Roles:**
    * `administracion_de_roles()`: Muestra la lista de roles y un formulario para crear nuevos roles.
    * `get_role()`: Obtiene la información de un rol específico.
    * `crear_rol()`: Crea un nuevo rol.
    * `delete_role()`: Elimina un rol.
    * `editar_rol()`: Edita un rol existente.
* **Administración de Usuarios:**
    * `administracion_de_usuarios()`: Muestra la lista de usuarios y un formulario para crear nuevos usuarios.
    * `get_user()`: Obtiene la información de un usuario específico.
    * `editar_usuario()`: Edita un usuario existente.
    * `eliminar_usuario()`: Elimina un usuario.
* **Administración de Proveedores:**
    * `suppliers_management()`: Muestra la lista de proveedores y un formulario para crear nuevos proveedores.
    * `get_supplier()`: Obtiene la información de un proveedor específico.
    * `create_supplier()`: Crea un nuevo proveedor.
    * `edit_supplier()`: Edita un proveedor existente.
    * `delete_supplier()`: Elimina un proveedor.
    * `export_suppliers()`: Exporta la lista de proveedores a un archivo Excel.
    * `import_suppliers()`: Importa proveedores desde un archivo Excel.

**Ejemplo de validación de formulario con validador customizado:**

```python
class NoRUTDuplicateValidator:
    def __call__(self, form, field):
        # Lógica para verificar si el RUT ya existe
```


### home.py

Este archivo define las rutas para la página de inicio de la aplicación.

**Funcionalidades:**

* **`index()`:** Redirige a la página de inicio de sesión (`/login`).
* **`home()`:** Define la ruta `/home` para la página de inicio principal.
    * Requiere que el usuario haya iniciado sesión y tenga el rol de "desarrollador".
    * Obtiene las recomendaciones del día utilizando `DayRecommendation.get_all`.
    * Filtra las recomendaciones según una consulta de búsqueda opcional.
    * Calcula la cantidad total de recomendaciones y productos.
    * Agrupa las recomendaciones por proveedor y calcula la cantidad de recomendaciones, productos y el costo total por proveedor.
    * Renderiza la plantilla `home.html` con los datos obtenidos.

**Ejemplo de paginación:**

```python
per_page = 10
total_pages = ceil(total_recommendations / per_page)
start = (page - 1) * per_page
end = start + per_page
recommendations = order_recommendations[start:end]
```

### human_resources.py

Este archivo define las rutas para la gestión de recursos humanos, incluyendo la gestión de empleados y el registro de horas extra.

**Funcionalidades:**

* **Gestión de Empleados:**
    * `employees_management()`: Muestra la lista de empleados y un formulario para crear nuevos empleados.
    * `get_employee()`: Obtiene la información de un empleado específico.
    * `create_employee()`: Crea un nuevo empleado.
    * `edit_employee()`: Edita un empleado existente.
    * `delete_employee()`: Elimina un empleado.
* **Gestión de Horas Extra:**
    * `overtime_hours_management()`: Muestra el registro de horas extra de un empleado para un mes específico.
    * `update_overtime_record()`: Actualiza un registro de horas extra.
    * `delete_overtime_record()`: Elimina un registro de horas extra.
    * `confirm()`: Confirma o retira la confirmación de un registro de horas extra.
    * `assign_holiday_day()`: Asigna o retira la asignación de un día como feriado.
    * `mark_as_vacation()`: Marca o retira la marca de un día como vacaciones pagadas.
    * `mark_as_absence()`: Marca o retira la marca de un día como ausencia (permiso no pagado).


**Ejemplo de validación de formulario con validador customizado:**

```python
class RUNValidator:
    def __call__(self, form, field):
        if not rut_chile.is_valid_rut(field.data):
            raise ValidationError("Invalid RUN.")
```

### reportes.py

Este archivo define las rutas para la generación de reportes.

**Funcionalidades:**

* `descargar_pdf()`: Define la ruta `/descargar_pdf` para descargar un PDF de ejemplo.
* `reporte_desempeño()`: Define la ruta `/reporte_desempeño` para mostrar la página del reporte de desempeño.

**Ejemplo de generación de PDF con pdfkit:**

```python
pdf = pdfkit.from_string(contenido_html, False, options=options)
```

### tables.py

Este archivo define las rutas para las tablas de datos, principalmente la tabla de productos.

**Funcionalidades:**

* `get_products()`: Define la ruta `/productos` para mostrar la tabla de productos.
    * Implementa la paginación para mostrar los productos en varias páginas.
    * Permite filtrar los productos por una consulta de búsqueda.
* `product_detail()`: Define la ruta `/productos/<variant_id>` para mostrar el detalle de un producto específico.
    * Obtiene la información del producto utilizando `Product.filter_product`.
    * Renderiza la plantilla `product_detail.html` con los datos del producto.
* `change_supplier()`: Define la ruta `/productos/<variant_id>/cambio_proveedor` (POST) para cambiar el proveedor de un producto.
* `change_activation_state()`: Define la ruta `/actualizar_estado_activacion/<variant_id>` (POST) para cambiar el estado de activación de un producto.

**Ejemplo de filtrado de datos:**

```python
filtered_products = Product.filter_products(session.get('search_query', ''))
```

## Conclusiones sobre la carpeta `/routes`

La carpeta `/routes` es fundamental para la aplicación, ya que define la estructura y la lógica de navegación de la misma. Al analizar los archivos dentro de esta carpeta, se pueden extraer las siguientes conclusiones:

**1. Organización Modular:** La carpeta está bien organizada, con cada archivo dedicado a un área específica de la aplicación (autenticación, compras, recursos humanos, etc.). Esto facilita la comprensión del código y su mantenimiento.

**2. Uso de Decoradores:** Se utilizan decoradores como `@requires_roles` para controlar el acceso a ciertas rutas en función del rol del usuario, lo que mejora la seguridad de la aplicación.

**3. Interacción con la API:** La aplicación interactúa con una API externa para obtener información de productos y enviar datos de recepción. Se utilizan clases como `ProductSearch` y `ReceptionPost` para encapsular la lógica de comunicación con la API.

**4. Manejo de Formularios:** Se utilizan formularios para recopilar información del usuario, como en el inicio de sesión, registro, creación de empleados y proveedores. Se implementan validaciones en los formularios para asegurar la integridad de los datos.

**5. Generación de Reportes:** Se utiliza la biblioteca `pdfkit` para generar reportes en formato PDF, lo que permite a los usuarios descargar información relevante en un formato fácil de compartir.

**6. Gestión de Datos:** La aplicación maneja datos de diferentes entidades, como productos, proveedores, empleados, carros de compra, etc. Se utilizan clases de modelo para interactuar con la base de datos y realizar operaciones CRUD (crear, leer, actualizar, eliminar).

**7. Análisis de Datos:** Se implementan funcionalidades para analizar datos, como el análisis de rendimiento de las compras en `compras.py`. Esto permite a los usuarios obtener información valiosa para la toma de decisiones.

**8. Uso de Sesiones:** Se utilizan sesiones para almacenar información temporal del usuario, como la consulta de búsqueda en la página de inicio.

**9. Manejo de Errores:** Se implementan mecanismos para manejar errores, como la captura de excepciones y la visualización de mensajes de error al usuario.

**En general, la carpeta `/routes` demuestra una buena práctica de desarrollo web, con una estructura organizada, código legible y funcionalidades bien definidas.** La aplicación se beneficia de la modularidad, el uso de decoradores, la interacción con la API, el manejo de formularios, la generación de reportes, la gestión de datos, el análisis de datos, el uso de sesiones y el manejo de errores. 

**Recomendaciones:**

* Se podría mejorar la documentación del código, incluyendo comentarios más detallados en las funciones y clases.
* Se podría implementar un sistema de logging para registrar eventos importantes y facilitar la depuración de errores.
* Se podría considerar la implementación de pruebas unitarias para asegurar la calidad del código.

**Conclusión final:** La carpeta `/routes` es un componente crucial de la aplicación web, que define su funcionalidad y su interacción con el usuario. El código está bien organizado y escrito, lo que facilita su mantenimiento y evolución futura. 
