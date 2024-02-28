import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import plotly.graph_objects as go

from math import ceil
from models.productos import Product
from models.pay_dates import PayDates
from models.model_cart import ModelCart
from models.price_list import PriceList
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

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
        categories = ['Estimado', 'Hoy']
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
        fig.add_trace(go.Bar(name='Costo Total', x=categories, y=[costs, costs], marker_color='#ffc107'))

        # Tax
        fig.add_trace(go.Bar(name='IVA', x=categories, y=[taxes_estimated, taxes_today], marker_color='#dc3545'))

        # Net Margin
        fig.add_trace(go.Bar(name='Margen Neto Estimado', x=['Estimado'], y=[net_margins_estimated], marker_color='salmon'))
        fig.add_trace(go.Bar(name='Margen Neto Actual', x=['Hoy'], y=[net_margins_today], marker_color='tomato'))

        # Adjusting layout for a stacked bar chart
        fig.update_layout(
            barmode='stack',
            title_text="Comparación de Costos, IVA y Márgenes Netos (Estimado vs. Hoy)",
            yaxis=dict(tickformat=',')  # Adjusting tick format to display full numbers
        )

        # fig.show()
        return fig.to_json()

    def distribucion_productos(self, margin_product_info):
        # Extracción de etiquetas (IDs de producto) y valores (cantidades y costo total)
        labels = [str(key) for key in margin_product_info.keys()]
        quantities = [info['product_quantity'] for info in margin_product_info.values()]
        total_costs = [info['total_cost'] for info in margin_product_info.values()]

        # Creación de los subplots
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

        # Gráfico de dona para la cantidad de productos
        fig.add_trace(go.Pie(labels=labels, values=quantities, name="", hole=.4), 1, 1)

        # Gráfico de dona para el costo total de los productos
        fig.add_trace(go.Pie(labels=labels, values=total_costs, name="", hole=.4), 1, 2)

        # Ajustes finales del layout
        fig.update_layout(title_text='Distribución de Productos por Cantidad y Costo Total')

        # Mostrar el gráfico
        # fig.show()
        return fig.to_json()

    def distribucion_productos_valores(self, margin_product_info):
        # Extracción de etiquetas (IDs de producto) y valores (cantidades y costo total)
        labels_estimados = [str(key) for key in margin_product_info.keys()]
        estimados = [info['estimated_revenue'] for info in margin_product_info.values()]
        hoy = [info['total_revenue_today'] for info in margin_product_info.values()]
        faltante = sum(estimados) - sum(hoy)

        labels = labels_estimados.copy()
        labels.append('Faltante')

        hoy.append(faltante)

        # Creación de los subplots
        fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])

        fig.add_trace(go.Pie(labels=labels_estimados, values=estimados, name="", hole=.4), 1, 1)

        fig.add_trace(go.Pie(labels=labels, values=hoy, name="", hole=.4), 1, 2)

        # Ajustes finales del layout
        fig.update_layout(title_text='Distribución de Productos por Venta Estimada y Venta hasta Hoy')

        # Mostrar el gráfico
        # fig.show()
        return fig.to_json()

    def barra_progreso(self, sales_evaluation):
        # Identificando el último término de pago y extrayendo la cantidad total vendida y la cantidad máxima
        latest_term = max(sales_evaluation['pay_terms'].keys())
        total_sold = sales_evaluation['pay_terms'][latest_term]['total_products_sold_up_to_date_general']
        max_quantity = sales_evaluation['product_quantity']

        # Creando el gráfico de barra de progreso
        fig = go.Figure(go.Bar(
            x=[total_sold, max_quantity - total_sold],  # Datos para el total vendido y el restante hacia la meta
            y=[''],
            orientation='h',
            marker=dict(color=["green", "lightgrey"]),  # Color verde para lo vendido, gris para lo restante
            hoverinfo="x",  # Mostrar solo el valor en el hover
        ))

        # Ajustes del layout para simular una barra de progreso
        fig.update_layout(
            title_text=f"Progreso de Ventas: {total_sold} / {max_quantity}",
            xaxis=dict(showgrid=False, showticklabels=True, tickformat=',', range=[0, max_quantity]),
            yaxis=dict(showticklabels=False),
            showlegend=False,
            barmode='stack'
        )

        # Mostrar el gráfico
        # fig.show()
        return fig.to_json()
    
    def roi_por_productos(self, margin_product_info):
        # Preparando los datos para la tabla
        product_ids = [f"{prod[0]}" for prod in margin_product_info.keys()]  # Creación de IDs de producto
        roi_today = [round(margin_product_info[prod]['net_margin_percentage_today'] / 100, 2) for prod in margin_product_info.keys()]
        roi_estimated = [round(margin_product_info[prod]['net_margin_percentage_estimated'] / 100, 2) for prod in margin_product_info.keys()]

        # Creación de la tabla
        fig = go.Figure(data=[go.Table(
            header=dict(values=['Product ID', 'ROI Today', 'ROI Estimated'],
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[product_ids, roi_today, roi_estimated],
                    fill_color='lavender',
                    align='left'))
        ])

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
                    'valor_unitario': sale['valor_unitario'],
                })

        sales_data = []
        for sale in ventas_list:
            sales_data.append((sale['fecha'], sale['cantidad'] * sale['valor_unitario']))

        sales_data_df = pd.DataFrame(sales_data, columns=['Date', 'TotalSales'])
        sales_data_df['Date'] = pd.to_datetime(sales_data_df['Date'])

        # Generar rango de fechas desde la fecha de recepción hasta la última fecha de venta
        start_date = sales_evaluation['reception_date']
        end_date = sales_data_df['Date'].max()
        date_range = pd.date_range(start=start_date, end=end_date)

        # Asegurar que todas las fechas estén en el DataFrame, rellenando con 0 donde no haya ventas
        sales_data_grouped = sales_data_df.groupby(sales_data_df['Date'].dt.date).agg({'TotalSales': 'sum'}).reindex(date_range, fill_value=0).reset_index().rename(columns={'index': 'Date'})
        sales_data_grouped['CumulativeTotalSales'] = sales_data_grouped['TotalSales'].cumsum()

        # Fechas de los plazos de pago para líneas verticales
        pay_terms_dates = [term_info['pay_date'] for term_key, term_info in sales_evaluation['pay_terms'].items()]

        # Utilizar CumulativeTotalSales para el gráfico
        fig = go.Figure()

        # Añadir las ventas acumuladas diarias como una línea
        fig.add_trace(go.Scatter(x=sales_data_grouped['Date'], y=sales_data_grouped['CumulativeTotalSales'], mode='lines', name='Cumulative Daily Sales'))

        # Añadir líneas horizontales para total_cost y estimated_revenue
        # Asegúrate de que margin_info y pay_terms_dates están definidos como en tu entorno
        fig.add_hline(y=margin_info['total_cost'], line_dash="dot", annotation_text="Total Cost", annotation_position="bottom right")
        fig.add_hline(y=margin_info['estimated_revenue'], line_dash="dot", annotation_text="Estimated Revenue", annotation_position="top right")

        # Añadir líneas verticales para los plazos de pago
        for pay_date in pay_terms_dates:
            fig.add_vline(x=pay_date, line_dash="dash", line_color="grey")

        dates_numeric = np.array([mdates.date2num(date) for date in sales_data_grouped['Date']])
        sales = sales_data_grouped['CumulativeTotalSales'].values

        # Calcular los coeficientes de la regresión lineal
        slope, intercept = np.polyfit(dates_numeric, sales, 1)

        # Calcular los valores de la línea de tendencia
        trend_line = slope * dates_numeric + intercept

        # Convertir fechas numéricas de vuelta a formato de fecha para Plotly
        trend_dates = [mdates.num2date(date_num) for date_num in dates_numeric]

        # Añadir la línea de tendencia al gráfico
        fig.add_trace(go.Scatter(x=trend_dates, y=trend_line, mode='lines', name='Trend Line'))

        min_date = sales_data_grouped['Date'].min()
        max_date = pay_terms_dates[-1]

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
                    text=f"Estimated Revenue: {round(margin_info['estimated_revenue'], 2):,}",
                    font=dict(family='Arial', size=12),
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.8)'
                ),
                # Anotación para total_cost
                dict(
                    xref='paper', x=0.95, y=margin_info['total_cost'],
                    xanchor='right', yanchor='bottom',
                    text=f"Total Cost: {margin_info['total_cost']:,}",
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
            title='Product Sales and Financial Milestones',
            xaxis_title='Date',
            yaxis_title='Cumulative Sales',
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
    # print(margin_info[11])
    # print(margin_info[12])
    # print(margin_info[13])
    # print("-")

    margin_product_info = buys.calculate_net_margin_per_product()
    print(margin_product_info)
    print("-")
    # cart_ids_to_find = {11, 12, 13}
    # filtered_entries = {key: value for key, value in margin_product_info.items() if key[1] in cart_ids_to_find}
    # print(filtered_entries)

    sales_evaluation = buys.evaluate_sales_by_payment_term()
    print(sales_evaluation)
    print("-")

    # buys.create_barras_apiladas(margin_info[11])
    # buys.distribucion_productos_valores(margin_product_info)
    # buys.barra_progreso(sales_evaluation[ids])
    # buys.roi_por_productos(margin_product_info)
    # buys.breakeven_de_compra(margin_info[ids], margin_product_info, sales_evaluation[ids])