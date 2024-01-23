import json
import pandas as pd

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, or_, cast

from databases.base import Base
from databases.session import AppSession
from services.stock_manager.simple.test import predict

from models.supplier import Supplier
from models.shipping import Shipping
from models.price_list import PriceList
from models.document import DocumentDetail
from models.reception import ReceptionDetail
from models.consumption import ConsumptionDetail
from models.day_recommendation import DayRecommendation

def format_number(number):
    return "${:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

def format_decimal(number):
    return "{:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

class Product(Base):
    __tablename__ = 'productos'

    variant_id = Column(Integer, primary_key=True)
    type = Column(String(255))
    description = Column(String(255))
    sku = Column(String(255))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))

    stock = relationship("ProductStock", uselist=False, back_populates="product")
    consumption_details = relationship("ConsumptionDetail", back_populates="product")
    reception_details = relationship("ReceptionDetail", back_populates="product")
    document_details = relationship("DocumentDetail", back_populates="product")
    price_list = relationship("PriceList", back_populates="product")
    supplier = relationship("Supplier", back_populates="products")
    day_recommendation = relationship("DayRecommendation", back_populates="product")

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
                    supplier = product.supplier
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
                        cast(Product.variant_id, String).ilike(search_query),
                        Product.type.ilike(search_query),
                        Product.sku.ilike(search_query),
                        Product.description.ilike(search_query),
                        Product.supplier.has(Supplier.trading_name.ilike(search_query))
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
                    supplier = product.supplier
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
                stock = product.stock.__dict__

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
                    df_salidas = create_empty_dataframe(['fecha', 'salida'])
                else:
                    df_salidas = pd.concat([df_consumos, df_ventas])[['fecha', 'cantidad']].rename(columns={'cantidad': 'salida'})

                df_unificado = pd.merge(df_entradas, df_salidas, on='fecha', how='outer').fillna(0)

                df_unificado = df_unificado.sort_values('fecha')
                df_unificado['stock_actual'] = df_unificado['entrada'] - df_unificado['salida']
                df_unificado['stock_actual'] = df_unificado['stock_actual'].cumsum()

                # Crear el DataFrame del Kardex
                df_kardex = df_unificado[['fecha', 'entrada', 'salida', 'stock_actual']]
                df_kardex['entrada'] = df_kardex['entrada'].astype(int)
                df_kardex['salida'] = df_kardex['salida'].astype(int)
                df_kardex['stock_actual'] = df_kardex['stock_actual'].astype(int)
                kardex = df_kardex.to_dict('records')

                services = {'SERVICIO DE TALLER', 'SERVICIOS', 'SERVICIOS DE TALLER'}
                if analysis and product.type not in services and len(df_kardex) > 1:
                    prediction = predict(df_kardex)
                else:
                    prediction = None

                product_data = {
                    **product.__dict__,
                    "supplier": product.supplier.__dict__,
                    "stock": stock,
                    "reception_details_list": reception_details_list,
                    "consumption_details_list": consumption_details_list,
                    "sales_list": sales_list,
                    "last_net_cost": last_net_cost,
                    "price_list": price_list,
                    "kardex": kardex,
                    "df_kardex": df_kardex,
                    "prediction": prediction
                }

                return product_data, prediction  # Return the product's attributes directly
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
        
