## DECORADORES

Esta carpeta contiene decoradores que se utilizan para agregar funcionalidades adicionales a las funciones de la aplicación. 

### Archivo: roles.py

Este archivo contiene el decorador `requires_roles`.

**Propósito:**

El decorador `requires_roles` se utiliza para restringir el acceso a ciertas funciones solo a usuarios con roles específicos. 

**Funcionamiento:**

* Recibe una lista de roles como argumento.
* Verifica si el usuario actual está autenticado. Si no lo está, lo redirige a la página de inicio de sesión.
* Realiza una consulta a la base de datos para obtener el rol del usuario actual.
* Verifica si el rol del usuario está en la lista de roles permitidos o si el usuario es un superadministrador. Si no lo es, muestra una plantilla de error "alerta_permisos_usuarios.html".
* Si el usuario tiene el rol requerido, permite que la función decorada se ejecute.

**Ejemplo de uso:**

```python
from decorators.roles import requires_roles

@requires_roles('administrador', 'editor')
def editar_articulo():
  # Código para editar un artículo
  pass
```

En este ejemplo, la función `editar_articulo` solo será accesible para usuarios con el rol de "administrador" o "editor".

**Extracto importante:**

```python
if not user_with_role or user_with_role.role.description not in roles and user_with_role.id_role != superadmin_id:
    return render_template('alerta_permisos_usuarios.html')
```

Este fragmento de código verifica si el usuario tiene el rol requerido o si es un superadministrador. Si no cumple ninguna de estas condiciones, se muestra la plantilla de error.

**Nota:**

El decorador `requires_roles` utiliza Flask-Login para la autenticación y SQLAlchemy para la interacción con la base de datos. 
