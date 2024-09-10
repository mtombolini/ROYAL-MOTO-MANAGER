# PLANTILLAS HTML

Esta carpeta contiene todas las plantillas HTML utilizadas en la aplicación web. Las plantillas están organizadas en subdirectorios según su funcionalidad y propósito dentro de la aplicación.

## Estructura de la Carpeta

- **auth/**: Contiene las plantillas para la autenticación de usuarios (login y registro).
  - **login.html**: Plantilla para la página de inicio de sesión.
  - **register.html**: Plantilla para la página de registro.

- **configuraciones/**: Contiene plantillas relacionadas con la configuración de la aplicación, como la administración de usuarios, roles y proveedores.
  - **administracion_de_usuarios/**: Plantillas para la edición y creación de usuarios.
  - **administracion_de_roles/**: Plantillas para la edición y creación de roles.
  - **suppliers_management/**: Plantillas para la edición y gestión de proveedores.

- **human_resources/**: Plantillas relacionadas con la gestión de recursos humanos.
  - **employees_management/**: Plantillas para la edición y creación de empleados.
  - **overtime_hours_management/**: Plantillas para la gestión de horas extras.

- **pdfs/**: Plantillas utilizadas para la generación de archivos PDF.
  - **emition_pdf.html**: Plantilla para la emisión de un PDF.

- **reportes/**: Plantillas para la generación de informes.

- **tables/**:  Plantillas que podrían contener componentes reutilizables o estructuras de tablas.

- **partials/**: Plantillas parciales que se incluyen en otras plantillas, como encabezados y pies de página.
  - **header.html**: Encabezado común para todas las páginas.
  - **footer.html**: Pie de página común para todas las páginas.

- **alerta_permisos_usuarios.html**: Plantilla para mostrar una alerta de permisos de usuario.
- **carro.html**: Plantilla para un carrito de compras o similar.
- **compras.html**: Plantilla para la gestión de compras.
- **espera.html**: Plantilla que posiblemente se muestre mientras se espera alguna acción.
- **home.html**: Plantilla para la página de inicio.
- **layout.html**: Plantilla base que define el diseño general de la aplicación.
- **recepcion_compra.html**: Plantilla para la recepción de compras.
- **rendimiento_compra.html**: Plantilla para la visualización del rendimiento de las compras. 

## Estilos Personalizados

Algunas plantillas pueden incluir estilos CSS personalizados para mejorar la apariencia y la usabilidad de los formularios y otros elementos de la interfaz de usuario.  Es recomendable revisar cada plantilla para identificar los estilos específicos utilizados.

## Uso de Formularios

Las plantillas utilizan formularios para interactuar con el backend de la aplicación. Los formularios están configurados para enviar datos a rutas específicas utilizando el método `POST`. Se pueden utilizar etiquetas de plantilla de Flask (si se utiliza Flask como framework) para generar los campos de formulario y manejar tokens CSRF.

## Ejemplo de Plantilla (Utilizando Flask)

```html
{% extends 'layout.html' %}

{% block title %}Título de la Página{% endblock %}

{% block customCSS %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/estilos.css') }}">
{% endblock %}

{% block body %}
<div class="container">
    <h1>Contenido de la Página</h1>
    <form action="{{ url_for('ruta.ejemplo') }}" method="post">
        {{ form.csrf_token }}
        <div class="mb-3">
            {{ form.campo.label(class="form-label") }}
            {{ form.campo(class="form-control") }}
        </div>
        <button type="submit" class="btn btn-primary">Enviar</button>
    </form>
</div>
{% endblock %}
