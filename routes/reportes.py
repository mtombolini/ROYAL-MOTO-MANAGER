from flask import Blueprint, render_template, request, make_response
import pdfkit

reportes_blueprint = Blueprint('reportes', __name__)

@reportes_blueprint.route('/descargar_pdf', methods=['POST'])
def descargar_pdf():
    tipo_reporte = request.form.get('tipo_reporte')
    contenido_html = f"<h1>Ejemplo de PDF para el tipo de reporte: {tipo_reporte}</h1>"

    # Configura las opciones para wkhtmltopdf
    options = {
        'page-size': 'Letter',
        'encoding': 'UTF-8',
    }

    # Genera el PDF
    pdf = pdfkit.from_string(contenido_html, False, options=options)

    # Configura la respuesta HTTP con el PDF y el encabezado adecuado
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte.pdf'

    return response


@reportes_blueprint.route('/reporte_desempeño')
def reporte_desempeño():
    # Tu lógica para obtener los vendedores
    vendedores = ["Vendedor 1", "Vendedor 2", "Vendedor 3"]
    
    return render_template('reportes/reporte_desempeño.html', vendedores=vendedores, page_title="Reporte de Desempeño")
