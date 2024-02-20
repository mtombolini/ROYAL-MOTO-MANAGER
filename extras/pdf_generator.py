from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_formatted_pdf(buffer, general_data, resume_data, detail_data):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=0
    )
    styles = getSampleStyleSheet()
    story = []
    
    col_widths = [
        1.5 * inch,
        4.5 * inch,
        0.85 * inch,
        0.90 * inch
    ]

    # Calcula el ancho total de la tabla
    table_width = sum(col_widths)

    # Estilo personalizado para el encabezado en la franja roja
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Title'],
        leading=30,
        backColor=colors.black,
        alignment=1,  # Centrado
        textColor=colors.whitesmoke,
        spaceBefore=10,
        spaceAfter=10,
        leftIndent=15,  # Asegúrate de que no haya indentación a la izquierda
        rightIndent=(doc.width - table_width) - 40,  # Ajusta la indentación derecha para alinear con el ancho de la tabla
        fontSize=20,
        fontName='Helvetica-Bold',
        borderRadius=2,
        borderWidth=4,
        borderColor=colors.black,
    )

    table_style = TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('BACKGROUND', (0,0), (-1,-1), colors.black),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.whitesmoke),
    ])

    # Carga la imagen
    image_path = 'static/img/logo_invert.png'
    logo = Image(image_path)
    logo.drawHeight = 0.5 * inch
    logo.drawWidth = 1 * inch

    # Texto que irá junto a la imagen
    text = "ROYAL MOTO SERVICE"
    formatted_text = Paragraph(text, style=header_style)

    # Crea la tabla para alinear la imagen y el texto
    header_table_data = [[logo, formatted_text]]
    header_table = Table(header_table_data, colWidths=[logo.drawWidth, doc.width - logo.drawWidth - 40], rowHeights=[logo.drawHeight])
    header_table.setStyle(table_style)

    # Añade la tabla al story
    story.append(header_table)

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        backColor=colors.lightgrey,  # Fondo gris
        alignment=1,  # Centrado
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=10,
        leftIndent=15,  # Asegúrate de que no haya indentación a la izquierda
        rightIndent=(doc.width - table_width) - 40,  # Ajusta la indentación derecha para alinear con el ancho de la tabla
        fontSize=14,
        borderRadius=5,
        borderWidth=5,
        borderColor=colors.lightgrey,
    )

    general_titles = ['ID del Carro:', 'Descripción:', 'Proveedor:', 'Fecha de Creación:', 'Estado:']
    resume_titles = ['Cantidad de Items:', 'Cantidad de Detalles:', 'Subtotal:', 'Impuestos:', 'Total:']

    # Tabla para los datos generales
    story.append(Paragraph('Información General:', section_title_style))
    general_table_data = [[title, info] for title, info in zip(general_titles, general_data)]
    general_table = Table(general_table_data, colWidths=[180, 80])
    general_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(general_table)
    story.append(Spacer(1, 12))

    # Tabla para el resumen
    story.append(Paragraph('Resumen de la Compra:', section_title_style))
    resume_table_data = [[title, info] for title, info in zip(resume_titles, resume_data)]
    resume_table = Table(resume_table_data, colWidths=[180, 80])
    resume_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(resume_table)
    story.append(Spacer(1, 12))

    
    
    cell_style = ParagraphStyle('CellStyle', wordWrap='LTR', 
                            fontSize=8,  # Adjust font size as needed
                            leading=8,  # Adjust leading (space between lines) as needed
                            alignment=1,  # Center alignment
                            fontName='Helvetica')

    # Configuración y estilo de la tabla para detalles
    story.append(Paragraph('Detalle de la Compra:', section_title_style))
    detail_headers = ['SKU', 'Descripción', 'Precio', 'Cantidad']


    detail_table_data = [detail_headers] + [row[1:] for row in detail_data]
    detail_table_data = [
        [Paragraph(cell, cell_style) if row_index > 0 else cell for cell in row]
        for row_index, row in enumerate(detail_table_data)
    ]
    detail_table = Table(detail_table_data, colWidths=col_widths)

    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.red),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('LONGTABLE', (0, 0), (-1, -1), None),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(detail_table)

    doc.build(story)