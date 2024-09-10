# DATABASES

Esta carpeta contiene los archivos relacionados con la configuración y gestión de la base de datos de la aplicación.

## Archivos

### base.py

Este archivo define la base declarativa para la creación de modelos de SQLAlchemy.

**Extracto importante:**

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

`Base` se utiliza como clase base para todos los modelos de la aplicación, permitiendo la definición de tablas y relaciones de la base de datos de forma orientada a objetos.

### drop_tables_reset.py

Este archivo contiene el script para eliminar todas las tablas de la base de datos. 

**Descripción:**

El script itera sobre una lista de nombres de tablas y, para cada una, ejecuta una consulta SQL `DROP TABLE` para eliminarla de la base de datos.

**Extracto importante:**

```python
def drop_table(table_name):
    with AppSession() as session:
        session.execute(text(f"DROP TABLE {table_name}"))
        session.commit()
        print(f"Tabla {table_name} eliminada exitosamente.")
```

**Uso:**

Este script se puede utilizar para reiniciar la base de datos a un estado inicial, eliminando todas las tablas existentes. Es importante tener precaución al ejecutar este script, ya que se perderán todos los datos almacenados en las tablas. Tambien es importante considerar que despues de usar este se puede usar init_db.py de /app.

### session.py

Este archivo se encarga de la configuración y creación de la sesión de la base de datos.

**Descripción:**

* Define la URL de conexión a la base de datos a partir de las variables de entorno o del archivo de configuración.
* Crea la base de datos si no existe, utilizando la URL de la base de datos por defecto.
* Crea el motor de SQLAlchemy y la fábrica de sesiones (`AppSession`).

**Extractos importantes:**

```python
def create_db(db_url, default_db_url):
    # ... crea la base de datos si no existe ...
```

```python
AppSession = sessionmaker(bind=app_engine)
```

`AppSession` se utiliza en toda la aplicación para interactuar con la base de datos, creando sesiones que permiten realizar consultas, insertar, actualizar y eliminar datos. 
