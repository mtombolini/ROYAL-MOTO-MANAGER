import random
import colorsys
import numpy as np
import pandas as pd
import plotly.express as px
import matplotlib.dates as mdates
import plotly.graph_objects as go
import matplotlib.colors as mcolors

from math import ceil
from datetime import datetime
from models.productos import Product
from models.pay_dates import PayDates
from models.model_cart import ModelCart
from models.price_list import PriceList

class BuysAnalysis:
    def __init__(self, cart_id):
        self.buys = [ModelCart.get_cart_by_id(cart_id)]
        self.payment_info = {}
        self.product_info = {}

    def create_info(self):
        for buy in self.buys:
            pay_dates = PayDates.get_pay_dates(buy.cart_id)

            fechas = [date.fecha_pago for date in pay_dates]
            fechas.sort()

            productos = ModelCart.get_cart_detail_by_id(buy.cart_id)

            self.payment_info[buy.cart_id] = {
                "variant_id_list": [(producto.variant_id, producto.id) for producto in productos[1]],
                "pay_dates_quantity": len(pay_dates),
                "product_quantity": buy.cantidad_productos,
                "products_per_month": ceil(buy.cantidad_productos / len(pay_dates)),
                "total_amount": buy.monto_neto,
                "first_date": buy.fecha_recepcion,
                "last_date": max(fechas),
                "pay_dates": fechas,
            }

            for producto in productos[1]:
                existing = Product.product_filter_by_id(producto.variant_id)
                if existing:
                    sale_list_today = Product.get_product_filtered_sales(producto.variant_id, buy.fecha_recepcion, datetime.now())
                    sale_list_payment_term = Product.get_product_filtered_sales(producto.variant_id, buy.fecha_recepcion, max(fechas))
                    self.product_info[producto.variant_id, buy.cart_id, producto.id] = {
                        "product_quantity": producto.cantidad,
                        "product_cost": producto.costo_neto,
                        "sales_today": sale_list_today,
                        "sales_payment_term": sale_list_payment_term
                    }

    def calculate_net_margin_per_purchase(self):
        margin_info = {}

        for cart_id, buy_info in self.payment_info.items():
            total_cost = buy_info['total_amount']  # Costo total de la compra
            total_revenue_today = 0  # Ingresos totales de las ventas relacionadas con esta compra
            total_revenue_term = 0  # Ingresos totales de las ventas relacionadas con esta compra

            # Comprobando si existe información de producto para esta compra
            estimated_revenue = 0
            for tuple_ids in buy_info['variant_id_list']:
                if (tuple_ids[0], cart_id, tuple_ids[1]) in self.product_info:
                    quantity = self.product_info[tuple_ids[0], cart_id, tuple_ids[1]]['product_quantity']
                    price_list_info = PriceList.get_price_list_by_variant_id(tuple_ids[0])
                    estimated_revenue_product = price_list_info[0].value / 1.19
                    estimated_revenue += estimated_revenue_product * quantity
                    sum_quantity_today = 0
                    sum_quantity_term = 0
                    product_sales_info_today = self.product_info[tuple_ids[0], cart_id, tuple_ids[1]]['sales_today']
                    product_sales_info_payment_term = self.product_info[tuple_ids[0], cart_id, tuple_ids[1]]['sales_payment_term']

                    # Sumar todos los ingresos de las ventas de productos de esta compra
                    for sale in product_sales_info_today:
                        if sum_quantity_today < quantity:
                            remaining_quantity = quantity - sum_quantity_today
                            considered_quantity = min(sale['cantidad'], remaining_quantity)
                
                            sale_revenue = sale['valor_unitario'] * considered_quantity
                            total_revenue_today += sale_revenue
                            
                            sum_quantity_today += considered_quantity
                            
                            if sum_quantity_today >= quantity:
                                break

                    for sale in product_sales_info_payment_term:
                        if sum_quantity_term < quantity:
                            remaining_quantity = quantity - sum_quantity_term
                            considered_quantity = min(sale['cantidad'], remaining_quantity)
                
                            sale_revenue = sale['valor_unitario'] * considered_quantity
                            total_revenue_term += sale_revenue
                            
                            sum_quantity_term += considered_quantity
                            
                            if sum_quantity_term >= quantity:
                                break

            # Calcular el margen neto para esta compra
            if total_cost > 0:  # Evitar división por cero
                net_margin_percentage_today = ((total_revenue_today - total_cost) / total_cost) * 100
                net_margin_percentage_term = ((total_revenue_term - total_cost) / total_cost) * 100
            else:
                net_margin_percentage_today = 0
                net_margin_percentage_term = 0


            # Almacenar la información del margen por compra
            margin_info[cart_id] = {
                'total_cost': total_cost,
                'product_quantity': buy_info['product_quantity'],
                'estimated_revenue': estimated_revenue,
                'tax_estimated': estimated_revenue * 0.19,
                'tax_today': total_revenue_today * 0.19,
                'total_revenue_term': total_revenue_term,
                'total_revenue_today': total_revenue_today,
                'net_margin_percentage_term': net_margin_percentage_term,
                'net_margin_percentage_today': net_margin_percentage_today,
            }

        return margin_info

    def evaluate_sales_by_payment_term(self):
        sales_evaluation = {}

        for cart_id, buy_info in self.payment_info.items():
            if cart_id not in sales_evaluation:
                sales_evaluation[cart_id] = {
                    'reception_date': buy_info['first_date'],
                    'product_quantity': buy_info['product_quantity'],
                    'pay_terms': {}
                }

            for term_index, pay_date in enumerate(sorted(buy_info['pay_dates']), start=1):
                term_key = str(term_index)  # Convertir term_index a cadena para usar como clave
                sales_evaluation[cart_id]['pay_terms'][term_key] = {
                    'pay_date': pay_date,
                    'total_products_sold_up_to_date_general': 0,
                    'expected_sales_by_term_general': 0,
                    'is_on_target_general': False,
                    'detail': []
                }

                total_products_sold_up_to_date = 0
                for tuple_ids in buy_info['variant_id_list']:
                    if (tuple_ids[0], cart_id, tuple_ids[1]) in self.product_info:
                        product_sales_info = self.product_info[tuple_ids[0], cart_id, tuple_ids[1]]['sales_today']
                        product_quantity = self.product_info[tuple_ids[0], cart_id, tuple_ids[1]]['product_quantity']

                        product_sales_count = sum(sale['cantidad'] for sale in product_sales_info if sale['fecha'] <= pay_date)
                        product_sales_count = min(product_sales_count, product_quantity)
                        total_products_sold_up_to_date += product_sales_count

                        expected_sales_by_term_product = ceil(product_quantity / len(buy_info['pay_dates'])) * term_index
                        is_on_target_product = product_sales_count >= expected_sales_by_term_product

                        sales_evaluation[cart_id]['pay_terms'][term_key]['detail'].append({
                            'product_id': tuple_ids[0],
                            'max_product_quantity': product_quantity,
                            'total_products_sold_up_to_date': product_sales_count,
                            'expected_sales_by_term': expected_sales_by_term_product,
                            'is_on_target': is_on_target_product
                        })

                sales_evaluation[cart_id]['pay_terms'][term_key]['total_products_sold_up_to_date_general'] = total_products_sold_up_to_date
                expected_sales_by_term_general = ceil(buy_info['product_quantity'] / len(buy_info['pay_dates'])) * term_index
                sales_evaluation[cart_id]['pay_terms'][term_key]['expected_sales_by_term_general'] = expected_sales_by_term_general
                sales_evaluation[cart_id]['pay_terms'][term_key]['is_on_target_general'] = total_products_sold_up_to_date >= expected_sales_by_term_general

        return sales_evaluation

    def calculate_net_margin_per_product(self):
        product_margin_info = {}

        for ids, product_sales_info in self.product_info.items():
            estimated_revenue = 0
            product_variant_id = ids[0]
            cart_id = ids[1]
            product_cost = product_sales_info['product_cost']  # Costo unitario del producto
            product_quantity = product_sales_info['product_quantity']  # Cantidad comprada del producto

            total_product_cost = product_cost * product_quantity  # Costo total de los productos comprados
            price_list_info = PriceList.get_price_list_by_variant_id(product_variant_id)
            estimated_revenue_product = price_list_info[0].value / 1.19
            estimated_revenue += estimated_revenue_product * product_quantity

            # Ingresos totales de las ventas de este producto, separados por hoy y a término
            total_revenue_today = 0
            total_revenue_term = 0

            sum_quantity_today = 0
            sum_quantity_term = 0

            # Procesar ventas de hoy
            for sale in product_sales_info['sales_today']:
                if sum_quantity_today < product_quantity:
                    remaining_quantity = product_quantity - sum_quantity_today
                    considered_quantity = min(sale['cantidad'], remaining_quantity)

                    sale_revenue = sale['valor_unitario'] * considered_quantity
                    total_revenue_today += sale_revenue

                    sum_quantity_today += considered_quantity

                    if sum_quantity_today >= product_quantity:
                        break

            # Procesar ventas a término
            for sale in product_sales_info['sales_payment_term']:
                if sum_quantity_term < product_quantity:
                    remaining_quantity = product_quantity - sum_quantity_term
                    considered_quantity = min(sale['cantidad'], remaining_quantity)

                    sale_revenue = sale['valor_unitario'] * considered_quantity
                    total_revenue_term += sale_revenue

                    sum_quantity_term += considered_quantity

                    if sum_quantity_term >= product_quantity:
                        break

            # Calcular el margen neto para este producto
            if total_product_cost > 0:  # Evitar división por cero
                net_margin_percentage_today = ((total_revenue_today - total_product_cost) / total_product_cost) * 100
                net_margin_percentage_term = ((total_revenue_term - total_product_cost) / total_product_cost) * 100
                net_margin_percentage_estimated = ((estimated_revenue - total_product_cost) / total_product_cost) * 100
            else:
                net_margin_percentage_today = 0
                net_margin_percentage_term = 0
                net_margin_percentage_estimated = 0

            if (product_variant_id, cart_id) not in product_margin_info:
                # Almacenar la información del margen por producto
                product_margin_info[product_variant_id, cart_id] = {
                    'total_cost': total_product_cost,
                    'product_cost': product_cost,
                    'product_quantity': product_quantity,
                    'estimated_revenue': estimated_revenue,
                    'total_revenue_today': total_revenue_today,
                    'total_revenue_term': total_revenue_term,
                    'net_margin_percentage_today': net_margin_percentage_today,
                    'net_margin_percentage_term': net_margin_percentage_term,
                    'net_margin_percentage_estimated': net_margin_percentage_estimated
                }
            else:
                # Actualizar la información del margen por producto
                product_margin_info[product_variant_id, cart_id]['total_cost'] += total_product_cost
                mean_cost = product_margin_info[product_variant_id, cart_id]['product_cost'] + product_cost / (product_margin_info[product_variant_id, cart_id]['product_quantity'] + product_quantity)
                product_margin_info[product_variant_id, cart_id]['product_cost'] = mean_cost
                product_margin_info[product_variant_id, cart_id]['product_quantity'] += product_quantity
                
        return product_margin_info

    def create_barras_apiladas(self, margin_info):
        categories = ['Ingresos Maximos', 'Ingresos Actuales']
        costs = margin_info['total_cost']
        taxes_estimated = margin_info['tax_estimated']
        net_margins_estimated = margin_info['estimated_revenue'] - costs

        costs_today = margin_info['total_cost']
        taxes_today = margin_info['tax_today']
        net_margins_today = margin_info['total_revenue_today'] - costs
        if net_margins_today < 0:
            if taxes_today <= abs(net_margins_today):
                taxes_today = 0
                costs_today = costs_today - abs(net_margins_today)
            else:
                taxes_today = taxes_today - abs(net_margins_today)
            net_margins_today = 0

        # Creating the figure
        fig = go.Figure()

        # Adding traces for each category
        # Cost
        fig.add_trace(go.Bar(name='Costo Total', x=categories, y=[costs, costs_today], marker_color='#ffc107'))

        # Tax
        fig.add_trace(go.Bar(name='IVA', x=categories, y=[taxes_estimated, taxes_today], marker_color='#dc3545'))

        # Net Margin
        fig.add_trace(go.Bar(name='Margen Neto Máximo', x=['Ingresos Maximos'], y=[net_margins_estimated], marker_color='salmon'))
        fig.add_trace(go.Bar(name='Margen Neto Actual', x=['Ingresos Actuales'], y=[net_margins_today], marker_color='tomato'))

        # Adjusting layout for a stacked bar chart
        fig.update_layout(
            barmode='stack',
            title_text="Comparación de Costos, IVA y Márgenes Netos (Máximo vs. Actual)",
            yaxis=dict(tickformat=',')  # Adjusting tick format to display full numbers
        )

        # fig.show()
        return fig.to_json()
    
    def distribuciones_productos(self, margin_product_info):
        labels_generales = []
        quantities = []
        total_costs = []
        estimados = []
        hoy = []
        for key, info in margin_product_info.items():
            sku = Product.product_filter_by_id(key[0]).sku
            labels_generales.append(str(sku))
            quantities.append(info['product_quantity'])
            total_costs.append(info['total_cost'])
            estimados.append(info['estimated_revenue'])
            hoy.append(info['total_revenue_today'])

        # Solo aplicar la lógica de "Otros" si hay más de 17 productos
        if len(labels_generales) > 17:
            # Ordenar hoy junto con sus etiquetas basado en hoy de mayor a menor
            hoy_sorted, labels_generales_sorted = zip(*sorted(zip(hoy, labels_generales), reverse=True))

            # Seleccionar los 17 mayores y acumular el resto en "Otros"
            hoy = list(hoy_sorted[:17]) + [sum(hoy_sorted[17:])]
            labels_generales = list(labels_generales_sorted[:17]) + ['Otros']

        labels_hoy = labels_generales.copy()
        faltante = sum(estimados) - sum(hoy)
        hoy.append(faltante)
        labels_hoy.append('Faltante')

        colores_generales = self.generar_colores_amarillo_rojo(len(labels_generales))
        # Asegurarse de tener colores para "Otros" y "Faltante" si es necesario
        colores_hoy = colores_generales + ['lightgrey'] * (len(labels_hoy) - len(labels_generales))

        # Crear las figuras con los colores específicos
        fig1 = go.Figure(data=[go.Pie(labels=labels_generales, values=quantities, hole=.4, marker=dict(colors=colores_generales))])
        fig2 = go.Figure(data=[go.Pie(labels=labels_generales, values=total_costs, hole=.4, marker=dict(colors=colores_generales))])
        fig3 = go.Figure(data=[go.Pie(labels=labels_generales, values=estimados, hole=.4, marker=dict(colors=colores_generales))])
        fig4 = go.Figure(data=[go.Pie(labels=labels_hoy, values=hoy, hole=.4, marker=dict(colors=colores_hoy))])

        fig1.update_layout(title_text='Distribución de Productos por Cantidad')
        fig2.update_layout(title_text='Distribución de Productos por Costo Total')
        fig3.update_layout(title_text='Distribución de Productos por Venta Maxima')
        fig4.update_layout(title_text='Distribución de Productos por Venta hasta Hoy')
        
        return fig1.to_json(), fig2.to_json(), fig3.to_json(), fig4.to_json()


    def generar_colores_amarillo_rojo(self, n):
        colores_hex = []
        min_saturation, max_saturation = 75, 90
        min_lightness, max_lightness = 50, 80
        
        for i in range(n):
            hue = (1/6) * (i / (n - 1))

            saturation = random.randint(min_saturation, max_saturation) / 100.0
            lightness = random.randint(min_lightness, max_lightness) / 100.0
            
            rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
            colores_hex.append('#' + ''.join(f'{int(c*255):02x}' for c in rgb))
        return colores_hex
    
    def barra_progreso(self, sales_evaluation):
        latest_term = max(sales_evaluation['pay_terms'].keys())
        total_sold = sales_evaluation['pay_terms'][latest_term]['total_products_sold_up_to_date_general']
        max_quantity = sales_evaluation['product_quantity']
        
        return {'total_sold': total_sold, 'max_quantity': max_quantity, 'percentage': round(total_sold / max_quantity * 100, 2)}
    
    def productos_barras_progreso(self, sales_evaluation):
        latest_term = max(sales_evaluation['pay_terms'].keys())
        products_info = sales_evaluation['pay_terms'][latest_term]['detail']
        products_progress = []
        for product_info in products_info:
            sku = Product.product_filter_by_id(product_info['product_id']).sku
            total_sold = product_info['total_products_sold_up_to_date']
            max_quantity = product_info['max_product_quantity']
            percentage = round(total_sold / max_quantity * 100, 2)
            products_progress.append({'product_sku': sku, 'total_sold': total_sold, 'max_quantity': max_quantity, 'percentage': percentage})
        return products_progress
    
    def roi_por_productos(self, margin_product_info):
        product_ids = [f"{Product.product_filter_by_id(prod[0]).sku}" for prod in margin_product_info.keys()]
        roi_today = [round(margin_product_info[prod]['net_margin_percentage_today'] / 100, 2) for prod in margin_product_info.keys()]
        roi_estimated = [round(margin_product_info[prod]['net_margin_percentage_estimated'] / 100, 2) for prod in margin_product_info.keys()]

        fig = go.Figure(data=[go.Table(
            header=dict(values=['Product ID', 'ROI Today', 'ROI Máximo'],
                        fill_color='black',
                        font=dict(color='white'),
                        align='left'),
            cells=dict(values=[product_ids, roi_today, roi_estimated],
                    fill_color='lightgrey',
                    align='left'))
        ])

        fig.update_layout(title_text='ROI por Producto (Actual vs. Máximo)')

        # Mostrar la tabla
        # fig.show()
        
        return fig.to_json()

    def breakeven_de_compra(self, margin_info, margin_product_info, sales_evaluation):
        product_ids = [prod[0] for prod in margin_product_info.keys()]
        dict_auxiliar = {key: value for key, value in self.product_info.items() if key[0] in product_ids}

        ventas_list = []
        for product_key, product_info in dict_auxiliar.items():
            for sale in product_info['sales_today']:
                ventas_list.append({
                    'producto_id': product_key[0],
                    'fecha': sale['fecha'],
                    'cantidad': sale['cantidad'],
                    'cantidad_maxima': margin_product_info[(product_key[0], product_key[1])]['product_quantity'],
                    'valor_unitario': sale['valor_unitario'],
                })

        cantidad_vendida_acumulada = {}
        ventas_ajustadas_list = []

        for venta in ventas_list:
            producto_id = venta['producto_id']
            cantidad_maxima = venta['cantidad_maxima']

            if producto_id not in cantidad_vendida_acumulada:
                cantidad_vendida_acumulada[producto_id] = 0
            
            cantidad_disponible = cantidad_maxima - cantidad_vendida_acumulada[producto_id]
            cantidad_ajustada = min(venta['cantidad'], cantidad_disponible)
            cantidad_vendida_acumulada[producto_id] += cantidad_ajustada
            
            if cantidad_ajustada > 0:
                ventas_ajustadas_list.append({
                    'producto_id': producto_id,
                    'fecha': venta['fecha'],
                    'cantidad': cantidad_ajustada,
                    'cantidad_maxima': cantidad_maxima,
                    'valor_unitario': venta['valor_unitario'],
                })

        sales_data = []
        for sale in ventas_ajustadas_list:
            sales_data.append((sale['fecha'], sale['cantidad'] * sale['valor_unitario']))

        sales_data_df = pd.DataFrame(sales_data, columns=['Date', 'TotalSales'])
        sales_data_df['Date'] = pd.to_datetime(sales_data_df['Date'])

        # Generar rango de fechas desde la fecha de recepción hasta la última fecha de venta
        start_date = sales_evaluation['reception_date']
        end_date = sales_data_df['Date'].max()
        
        if pd.isna(end_date):
            end_date = start_date + pd.Timedelta(days=30)
        date_range = pd.date_range(start=start_date, end=end_date)
        date_range_normalized = date_range.normalize()
        
        # Asegurar que todas las fechas estén en el DataFrame, rellenando con 0 donde no haya ventas
        sales_data_grouped = sales_data_df.groupby(sales_data_df['Date'].dt.date).agg({'TotalSales': 'sum'}).reindex(date_range_normalized, fill_value=0).reset_index().rename(columns={'index': 'Date'})
        sales_data_grouped['CumulativeTotalSales'] = sales_data_grouped['TotalSales'].cumsum()

        # Fechas de los plazos de pago para líneas verticales
        pay_terms_dates = [term_info['pay_date'] for term_key, term_info in sales_evaluation['pay_terms'].items()]

        # Utilizar CumulativeTotalSales para el gráfico
        fig = go.Figure()

        # Añadir las ventas acumuladas diarias como una línea
        fig.add_trace(go.Scatter(x=sales_data_grouped['Date'], y=sales_data_grouped['CumulativeTotalSales'], mode='lines', name='Ventas Acumuladas'))

        fig.add_hline(y=margin_info['total_cost'], line_dash="dot", annotation_text="Total Cost", annotation_position="bottom right")
        fig.add_hline(y=margin_info['estimated_revenue'], line_dash="dot", annotation_text="Estimated Revenue", annotation_position="top right")

        # Añadir líneas verticales para los plazos de pago
        for pay_date in pay_terms_dates:
            fig.add_vline(x=pay_date, line_dash="dash", line_color="grey")

        dates_numeric = np.array([mdates.date2num(date) for date in sales_data_grouped['Date']])
        sales = sales_data_grouped['CumulativeTotalSales'].values
        
        if np.all(sales == 0):
            slope = 0
            intercept = 0
        else:
            # Calcular los coeficientes de la regresión lineal
            slope, intercept = np.polyfit(dates_numeric, sales, 1)

        # Calcular los valores de la línea de tendencia
        trend_line = slope * dates_numeric + intercept

        # Convertir fechas numéricas de vuelta a formato de fecha para Plotly
        trend_dates = [mdates.num2date(date_num) for date_num in dates_numeric]

        # Añadir la línea de tendencia al gráfico
        fig.add_trace(go.Scatter(x=trend_dates, y=trend_line, mode='lines', name='Tendencia'))

        min_date = sales_data_grouped['Date'].min()
        max_date = pay_terms_dates[-1]

        date_range_extended = pd.date_range(start=start_date, end=max_date)
        optimal_sales_per_day = margin_info['estimated_revenue'] * 0.95 / (max_date - start_date).days
        optimal_sales_line = [optimal_sales_per_day * (date - start_date).days for date in date_range_extended]

        # Añadir la línea óptima al gráfico
        fig.add_trace(go.Scatter(x=date_range_extended, y=optimal_sales_line, mode='lines', name='Óptimo de Ventas', line=dict(color='green')))

        # Extiende estas fechas por 2 días en cada dirección
        extended_min_date = min_date - pd.Timedelta(days=2)
        extended_max_date = max_date + pd.Timedelta(days=2)
        
        # Actualiza el layout del gráfico para ajustar el rango del eje X
        fig.update_layout(
            annotations=[
                # Anotación para estimated_revenue
                dict(
                    xref='paper', x=0.95, y=margin_info['estimated_revenue'],
                    xanchor='right', yanchor='bottom',
                    text=f"Ganancia Máxima: {round(margin_info['estimated_revenue'], 2):,}",
                    font=dict(family='Arial', size=12),
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.8)'
                ),
                # Anotación para total_cost
                dict(
                    xref='paper', x=0.95, y=margin_info['total_cost'],
                    xanchor='right', yanchor='bottom',
                    text=f"Costo de la Compra: {margin_info['total_cost']:,}",
                    font=dict(family='Arial', size=12),
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.8)'
                )
            ],
            xaxis=dict(
                range=[extended_min_date, extended_max_date],
                showgrid=True, 
                gridwidth=1, 
                gridcolor='White'
            ),
            yaxis=dict(
                range=[0, margin_info['estimated_revenue'] * 1.1],
                showgrid=True, 
                gridwidth=1, 
                gridcolor='White',
                tickformat=',',  # Usa ',' para separar miles, mostrando números completos
            ),
            title='Analisis de Ventas (Breakeven)',
            yaxis_title='Ventas Acumuladas',
        )

        # Mostrar el gráfico
        # fig.show()
        return fig.to_json()

if __name__ == "__main__":
    ids = 12
    buys = BuysAnalysis(ids)
    print(buys.buys)
    buys.create_info()
    margin_info = buys.calculate_net_margin_per_purchase()
    print(margin_info)
    print("-")

    margin_product_info = buys.calculate_net_margin_per_product()
    print(margin_product_info)
    print("-")

    sales_evaluation = buys.evaluate_sales_by_payment_term()
    print(sales_evaluation)
    print("-")

    # buys.create_barras_apiladas(margin_info[ids])
    # buys.distribucion_productos_valores(margin_product_info)
    # buys.barra_progreso(sales_evaluation[ids])
    # buys.roi_por_productos(margin_product_info)
    # buys.breakeven_de_compra(margin_info[ids], margin_product_info, sales_evaluation[ids])
    # buys.distribuciones_productos(margin_product_info)