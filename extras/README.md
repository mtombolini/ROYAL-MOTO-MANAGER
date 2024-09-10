# EXTRAS

Esta carpeta contiene scripts y utilidades auxiliares para diversas tareas relacionadas con la aplicación.

## Archivos

### assertions.py

Este archivo define una ruta de API que devuelve el ID del rol de superadministrador. 

**Ejemplo de uso:**

```python
@api_blueprint.route('/get_superadmin_role_id')
def get_superadmin_id_role(session):
    return jsonify(
        superadmin_role_id=session.query(Role).filter_by(description="superadministrador").first().id_role,
    )
```

### backup_table.py

Este script permite exportar e importar datos de tablas específicas de la base de datos a archivos SQL.

**Funcionalidades:**

* `export_table_data_to_sql(table_name)`: Exporta los datos de la tabla especificada a un archivo SQL en la carpeta `backup`.
* `import_table_data_from_sql(file_path)`: Importa datos a la base de datos desde un archivo SQL.

**Ejemplo de uso:**

```python
# Exportar datos de la tabla 'carros_compras'
export_table_data_to_sql('carros_compras')

# Importar datos desde el archivo 'backup/carros_compras_backup.sql'
import_table_data_from_sql("backup/carros_compras_backup.sql")
```

### datatime.py

Este archivo contiene una función para reformatear fechas en formato de cadena.

**Funcionalidad:**

* `reformat_strftime(strf_date: str, from_format: str, to_format: str) -> str`: Convierte una fecha en formato de cadena de un formato a otro.

**Ejemplo de uso:**

```python
fecha_original = "2023-11-09 22:00:00"
fecha_reformateada = reformat_strftime(fecha_original, "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M")
print(fecha_reformateada)  # Salida: 09/11/2023 22:00
```

### generate_password.py

Este script genera un hash de contraseña utilizando la función `generate_password_hash` de Werkzeug.

**Funcionalidad:**

* `generate_password(password)`: Genera un hash de la contraseña proporcionada.

**Ejemplo de uso:**

```python
hash_contraseña = generate_password("mi_contraseña")
print(hash_contraseña) 
```

### init_product_activation.py

Este script inicializa la tabla `ProductActivation` en la base de datos, creando un registro para cada producto existente en la tabla `Product`.

**Funcionalidad:**

* `init_product_activation()`: Crea registros en la tabla `ProductActivation` para cada SKU de producto, estableciendo `is_active` en `True`.

### json_transformation.py

Este script exporta los datos de las tablas `product_supplier_association` y `suppliers` a archivos JSON, realizando una transformación en el campo `credit_term`.

**Funcionalidades:**

* `transform_credit_term(credit_term)`: Mapea los valores del campo `credit_term` a su equivalente en español.
* `get_json_data(table_name)`: Exporta los datos de la tabla especificada a un archivo JSON en la carpeta `backup`.

**Ejemplo de uso:**

```python
get_json_data('product_supplier_association') # Genera el archivo backup/product_supplier_association.json
get_json_data('suppliers') # Genera el archivo backup/suppliers.json
```

### print_archive.py

Este archivo no contiene código relevante, solo una instrucción `print("")`.

## Conclusiones

Los scripts en esta carpeta proporcionan funcionalidades auxiliares para la gestión de la base de datos, la generación de contraseñas, el manejo de fechas y la exportación de datos. 
