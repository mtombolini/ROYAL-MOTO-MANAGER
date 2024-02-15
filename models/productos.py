import json
import pandas as pd

from datetime import datetime, timedelta
from math import ceil

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, or_, cast

from databases.base import Base
from databases.session import AppSession
from services.stock_manager.simple.test import predict
from services.stock_manager.parameters_service import DAYS_OF_ANTICIPATION, DAYS_TO_LAST

from models.supplier import Supplier
from models.shipping import Shipping
from models.price_list import PriceList
from models.document import DocumentDetail
from models.reception import ReceptionDetail
from models.last_net_cost import LastNetCost
from models.consumption import ConsumptionDetail
from models.day_recommendation import DayRecommendation
from models.associations import product_supplier_association

def format_number(number):
    return "${:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

def format_decimal(number):
    return "{:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

class Product(Base):
    __tablename__ = 'productos'

    variant_id = Column(Integer, primary_key=True)
    type = Column(String(255))
    description = Column(String(255))
    sku = Column(String(255), unique=True)

    stock = relationship("ProductStock", uselist=False, back_populates="product")
    consumption_details = relationship("ConsumptionDetail", back_populates="product")
    reception_details = relationship("ReceptionDetail", back_populates="product")
    document_details = relationship("DocumentDetail", back_populates="product")
    price_list = relationship("PriceList", back_populates="product")
    day_recommendation = relationship("DayRecommendation", back_populates="product")
    last_net_cost = relationship("LastNetCost", uselist=False, back_populates="product")
    suppliers = relationship('Supplier', secondary=product_supplier_association, back_populates='products')

    @classmethod
    def product_filter_by_sku(cls, sku):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.sku == sku).first()
                if product is None:
                    return None, None, None
                return product, product.suppliers[0].rut, product.last_net_cost.net_cost
            except Exception as ex:
                print(ex)
                raise

    @classmethod
    def get_all_products_ids(cls):
        with AppSession() as session:
            try:
                products = session.query(cls).all()
                products_ids = [product.variant_id for product in products]
                return products_ids
            except Exception as ex:
                raise

    @classmethod
    def get_all_products(cls):
        with AppSession() as session:
            try:
                products = session.query(cls).all()
                products_data = [
                    {
                        key: value 
                        for key, value in product.__dict__.items() 
                        if not key.startswith('_')
                    }
                for product in products
                ]

                for product_data, product in zip(products_data, products):
                    supplier = product.suppliers
                    if supplier:
                        product_data['supplier_trading_name'] = supplier.trading_name
                    else:
                        product_data['supplier_trading_name'] = None

                return products_data
            except Exception as ex:
                raise

    @classmethod
    def filter_products(cls, search_query):
        with AppSession() as session:
            try:
                search_query = f"%{search_query.lower()}%"
                products = session.query(cls).filter(
                    or_(
                        cast(cls.variant_id, String).ilike(search_query),
                        cls.type.ilike(search_query),
                        cls.sku.ilike(search_query),
                        cls.description.ilike(search_query),
                        cls.suppliers.any(Supplier.trading_name.ilike(search_query))
                    )
                ).all()

                products_data = [
                    {
                        key: value
                        for key, value in product.__dict__.items()
                        if not key.startswith('_')
                    }
                for product in products
                ]

                for product_data, product in zip(products_data, products):
                    supplier = product.suppliers[0]
                    if supplier:
                        product_data['supplier_trading_name'] = supplier.trading_name
                    else:
                        product_data['supplier_trading_name'] = None

                return products_data
            except Exception as ex:
                raise

    @classmethod
    def filter_product(cls, variant_id, analysis=True):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()  # Retrieve a single product

                stock = cls.get_product_stock(variant_id)
                last_net_cost, reception_details_list, df = cls.get_product_reception(variant_id)
                consumption_details_list, df_consumos = cls.get_product_comsumptions(variant_id)
                sales_list, df_ventas = cls.get_product_sales(variant_id)
                price_list, df_precios = cls.get_product_price_list(variant_id, last_net_cost)

                if not df_ventas.empty:
                    df_ventas = df_ventas.drop_duplicates()

                def create_empty_dataframe(columns):
                    return pd.DataFrame(columns=columns)

                # Comprobar si los DataFrames están vacíos y crear DataFrames vacíos si es necesario
                if df.empty:
                    df_entradas = create_empty_dataframe(['fecha', 'entrada'])
                else:
                    df_entradas = df[['fecha', 'cantidad']].rename(columns={'cantidad': 'entrada'})

                if df_consumos.empty and df_ventas.empty:
                    df_salidas = create_empty_dataframe(['fecha', 'salida', 'tipo_salida'])
                else:
                    df_consumos['tipo_salida'] = 'consumo'
                    df_ventas['tipo_salida'] = 'venta'
                    df_salidas = pd.concat([df_consumos, df_ventas])[['fecha', 'cantidad', 'tipo_salida']].rename(columns={'cantidad': 'salida'})

                df_unificado = pd.merge(df_entradas, df_salidas, on='fecha', how='outer').fillna(0)

                df_unificado = df_unificado.sort_values('fecha')
                df_unificado['stock_actual'] = df_unificado['entrada'] - df_unificado['salida']
                df_unificado['stock_actual'] = df_unificado['stock_actual'].cumsum()

                # Crear el DataFrame del Kardex
                df_kardex = df_unificado[['fecha', 'entrada', 'salida', 'stock_actual', 'tipo_salida']]
                df_kardex['entrada'] = df_kardex['entrada'].astype(int)
                df_kardex['salida'] = df_kardex['salida'].astype(int)
                df_kardex['stock_actual'] = df_kardex['stock_actual'].astype(int)
                kardex = df_kardex.to_dict('records')

                services = {'SERVICIO DE TALLER', 'SERVICIOS', 'SERVICIOS DE TALLER'}
                if analysis and product.type not in services and len(df_kardex) > 1:
                    prediction, mean = predict(df_kardex)
                else:
                    prediction = None
                    mean = None

                today = datetime.now().date()
                stock_actual = stock['stock_lira'] + stock['stock_sobrexistencia']
                
                if mean is not None and mean != 0:
                    disponibilidad = ceil(stock_actual / mean)
                    if disponibilidad < 0:
                        disponibilidad = 0
                    fecha_disponibilidad = today + timedelta(days=disponibilidad)
                else:
                    disponibilidad = None
                    fecha_disponibilidad = None

                if mean is not None:
                    recommendation = ceil(mean * (DAYS_TO_LAST - DAYS_OF_ANTICIPATION))
                else:
                    recommendation = None
                    fecha_recommendation = None

                if mean is not None and mean != 0:
                    days_to_recommendation = ceil((stock_actual - mean * DAYS_OF_ANTICIPATION) / mean)
                    if days_to_recommendation < 0:
                        days_to_recommendation = 0
                    fecha_days_to_recommendation = today + timedelta(days=days_to_recommendation)
                else:
                    days_to_recommendation = None
                    fecha_days_to_recommendation = None


                product_data = {
                    **product.__dict__,
                    "supplier": product.suppliers[0].__dict__,
                    "stock": stock,
                    "reception_details_list": reception_details_list,
                    "consumption_details_list": consumption_details_list,
                    "sales_list": sales_list,
                    "last_net_cost": last_net_cost,
                    "price_list": price_list,
                    "kardex": kardex,
                    "df_kardex": df_kardex,
                    "prediction": prediction,
                    "disponibilidad": fecha_disponibilidad,
                    "recommendation": recommendation,
                    "days_to_recommendation": fecha_days_to_recommendation
                }

                return product_data, prediction  # Return the product's attributes directly
            except Exception as ex:
                raise

    @classmethod
    def get_product_stock(cls, variant_id):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()
                stock = product.stock.__dict__
                return stock
            except Exception as ex:
                raise

    @classmethod
    def get_product_reception(cls, variant_id, normal_search=True):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()
                data = []
                for reception_detail in product.reception_details:
                    reception = reception_detail.reception

                    if reception.document_type == "Sin Documento":
                        num = reception_detail.reception_id
                    else:
                        num = reception.document_number

                    if "GUÍA" in reception.document_type:
                        shipping = Shipping.seach_shipping_guide_by_number(f"{num}.0")
                        if shipping is not None and shipping["shipping_type"] != "Traslados internos (no constituye venta)":
                            data.append({
                            "fecha": reception.date,
                            "documento": reception.document_type + " " + str(num),
                            "tipo_de_documento": reception.document_type,
                            "numero_de_documento": num,
                            "oficina": reception.office,
                            "nota": reception.note,
                            "cantidad": reception_detail.quantity,
                            "costo_neto": reception_detail.net_cost,
                            "costo_neto_formated": format_number(reception_detail.net_cost)
                        })
                            
                    else:
                        data.append({
                            "fecha": reception.date,
                            "documento": reception.document_type + " " + str(num),
                            "tipo_de_documento": reception.document_type,
                            "numero_de_documento": num,
                            "oficina": reception.office,
                            "nota": reception.note,
                            "cantidad": reception_detail.quantity,
                            "costo_neto": reception_detail.net_cost,
                            "costo_neto_formated": format_number(reception_detail.net_cost)
                        })

                df = pd.DataFrame(data)
                if df.empty:
                    reception_details_list = []
                else:
                    reception_details_list = df.sort_values('fecha').to_dict('records')

                selected_document = None
                if not df.empty:
                    df = df.sort_values('fecha', ascending=False)
                    factura_recente = df[df['tipo_de_documento'] == 'Factura']
                    if not factura_recente.empty:
                        selected_document = factura_recente.iloc[0]
                    else:
                        sin_documento_recente = df[df['tipo_de_documento'] == 'Sin Documento']
                        if not sin_documento_recente.empty:
                            selected_document = sin_documento_recente.iloc[0]
                        else:
                            selected_document = None

                if selected_document is not None:
                    last_net_cost = {
                        "fecha": selected_document['fecha'],
                        "costo_neto": selected_document['costo_neto'],
                        "costo_neto_formated": selected_document['costo_neto_formated']
                    }
                else:
                    last_net_cost = {
                        "fecha": None,
                        "costo_neto": None,
                        "costo_neto_formated": None
                    }

                if not normal_search:
                    LastNetCost.create_last_net_cost(
                        variant_id, 
                        last_net_cost['costo_neto_formated'], 
                        last_net_cost['costo_neto'], 
                        last_net_cost['fecha'])

                return last_net_cost, reception_details_list, df
            except Exception as ex:
                raise

    @classmethod
    def get_product_comsumptions(cls, variant_id):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()
                data_consumos = []
                for consumption_detail in product.consumption_details:
                    consumption = consumption_detail.consumption
                    data_consumos.append({
                        "fecha": consumption.date,
                        "oficina": consumption.office,
                        "nota": consumption.note,
                        "cantidad": consumption_detail.quantity,
                        "costo_neto": consumption_detail.net_cost,
                        "costo_neto_formated": format_number(consumption_detail.net_cost)
                    })

                df_consumos = pd.DataFrame(data_consumos)
                if df_consumos.empty:
                    consumption_details_list = []
                else:
                    consumption_details_list = df_consumos.sort_values('fecha').to_dict('records')

                return consumption_details_list, df_consumos
            except Exception as ex:
                raise
                
    @classmethod
    def get_product_sales(cls, variant_id):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()
                data_ventas = []
                for document_detail in product.document_details:
                    document = document_detail.document
                    sales = document.sales
                    if sales != []:
                        for sale in sales:
                            sale_model = sale.sale
                            data_ventas.append({
                                "fecha": document.date,
                                "documento": document.document_type + " " + document.document_number,
                                "tipo_de_documento": document.document_type,
                                "numero_de_documento": document.document_number,
                                "oficina": document.office,
                                "cantidad": document_detail.quantity,
                                "valor_unitario": document_detail.net_unit_value,
                                "valor_unitario_formated": format_number(document_detail.net_total_value),
                                "valor_total": document_detail.net_total_value * document_detail.quantity,
                                "valor_total_formated": format_number(document_detail.net_total_value * document_detail.quantity)
                            })

                df_ventas = pd.DataFrame(data_ventas)
                if df_ventas.empty:
                    sales_list = []
                else:
                    sales_list = df_ventas.drop_duplicates().sort_values('fecha').to_dict('records')

                return sales_list, df_ventas
            except Exception as ex:
                raise

    @classmethod
    def get_product_price_list(cls, variant_id, last_net_cost):
        with AppSession() as session:
            try:
                product = session.query(cls).filter(cls.variant_id == variant_id).first()
                data_precios = []
                for price_list in product.price_list:
                    data_precios.append({
                        "name": price_list.name,
                        "valor": price_list.value,
                        "valor_formated": format_number(price_list.value),
                        "factor_ponderador": (price_list.value / last_net_cost['costo_neto']) if (last_net_cost['costo_neto'] != None) and (last_net_cost['costo_neto'] != 0) else "Indefinido",
                        "factor_ponderador_formated": format_decimal(price_list.value / last_net_cost['costo_neto']) if (last_net_cost['costo_neto'] != None) and (last_net_cost['costo_neto'] != 0) else "Indefinido"
                    })

                df_precios = pd.DataFrame(data_precios)
                if df_precios.empty:
                    price_list = []
                else:
                    price_list = df_precios.to_dict('records')
                
                return price_list, df_precios
            except Exception as ex:
                raise
                

class ProductStock(Base):
    __tablename__ = 'productos_stock'

    variant_id = Column(Integer, ForeignKey('productos.variant_id'), primary_key=True)
    stock_lira = Column(Integer)
    stock_sobrexistencia = Column(Integer)
    
    # el nombre aquí 'producto' debe coincidir con el nombre de la relación en Product
    product = relationship("Product", back_populates="stock")

    @classmethod
    def get_all_stocks(cls):
        with AppSession() as session:
            try:
                stocks = session.query(cls).all()
                stocks_data = [
                    {
                        key: value 
                        for key, value in stock.__dict__.items() 
                        if not key.startswith('_')
                    } 
                for stock in stocks
                ]

                return stocks_data
            except Exception as ex:
                raise

    @classmethod
    def filter_stock(cls, variant_id):
        with AppSession() as session:
            try:
                stock = session.query(cls).filter(cls.variant_id == variant_id).first()  # Retrieve a single stock
                if stock:
                    return stock.__dict__  # Return the stock's attributes directly
                else:
                    return None  # Handle case where stock is not found
            except Exception as ex:
                raise
        