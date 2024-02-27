from models.model_cart import ModelCart
from models.price_list import PriceList
from models.pay_dates import PayDates
from models.productos import Product
from datetime import datetime
from math import ceil
import plotly.graph_objects as go
import matplotlib.pyplot as plt
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
                "variant_id_list": [producto.variant_id for producto in productos[1]],
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
                    self.product_info[producto.variant_id, buy.cart_id] = {
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
            for product_id in buy_info['variant_id_list']:
                if (product_id, cart_id) in self.product_info:
                    quantity = self.product_info[product_id, cart_id]['product_quantity']
                    price_list_info = PriceList.get_price_list_by_variant_id(product_id)
                    estimated_revenue_product = price_list_info[0].value
                    estimated_revenue += estimated_revenue_product * quantity
                    sum_quantity_today = 0
                    sum_quantity_term = 0
                    product_sales_info_today = self.product_info[product_id, cart_id]['sales_today']
                    product_sales_info_payment_term = self.product_info[product_id, cart_id]['sales_payment_term']

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
                for product_id in buy_info['variant_id_list']:
                    if (product_id, cart_id) in self.product_info:
                        product_sales_info = self.product_info[product_id, cart_id]['sales_today']
                        product_quantity = self.product_info[product_id, cart_id]['product_quantity']

                        product_sales_count = sum(sale['cantidad'] for sale in product_sales_info if sale['fecha'] <= pay_date)
                        product_sales_count = min(product_sales_count, product_quantity)
                        total_products_sold_up_to_date += product_sales_count

                        expected_sales_by_term_product = ceil(product_quantity / len(buy_info['pay_dates'])) * term_index
                        is_on_target_product = product_sales_count >= expected_sales_by_term_product

                        sales_evaluation[cart_id]['pay_terms'][term_key]['detail'].append({
                            'product_id': product_id,
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
            product_variant_id = ids[0]
            cart_id = ids[1]
            product_cost = product_sales_info['product_cost']  # Costo unitario del producto
            product_quantity = product_sales_info['product_quantity']  # Cantidad comprada del producto

            total_product_cost = product_cost * product_quantity  # Costo total de los productos comprados

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
            else:
                net_margin_percentage_today = 0
                net_margin_percentage_term = 0

            if (product_variant_id, cart_id) not in product_margin_info:
                # Almacenar la información del margen por producto
                product_margin_info[product_variant_id, cart_id] = {
                    'total_cost': total_product_cost,
                    'product_cost': product_cost,
                    'product_quantity': product_quantity,
                    'total_revenue_today': total_revenue_today,
                    'total_revenue_term': total_revenue_term,
                    'net_margin_percentage_today': net_margin_percentage_today,
                    'net_margin_percentage_term': net_margin_percentage_term
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

        fig.show()



if __name__ == "__main__":
    buys = BuysAnalysis(11)
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

    # buys.create_pie_charts(margin_info[11])
    # buys.create_pie_not_interactive(margin_info[11])
    # buys.create_barras_lado_a_lado(margin_info[11])
    buys.create_barras_apiladas(margin_info[11])