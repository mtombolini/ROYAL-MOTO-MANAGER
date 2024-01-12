from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
import pandas as pd

def format_number(number):
    return "${:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")

def format_decimal(number):
    return "{:,.2f}".format(number).replace(",", "X").replace(".", ",").replace("X", ".")


from models.consumption import ConsumptionDetail
from models.reception import ReceptionDetail
from models.document import DocumentDetail
from models.price_list import PriceList

class Product(Base):
    __tablename__ = 'productos'

    variant_id = Column(Integer, primary_key=True)
    type = Column(String(255))
    description = Column(String(255))
    sku = Column(String(255))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    
    # asegúrate de que 'stock' corresponda al nombre de la relación inversa en ProductStock
    stock = relationship("ProductStock", uselist=False, back_populates="product")
    consumption_details = relationship("ConsumptionDetail", back_populates="product")
    reception_details = relationship("ReceptionDetail", back_populates="product")
    document_details = relationship("DocumentDetail", back_populates="product")
    price_list = relationship("PriceList", back_populates="product")
    supplier = relationship("Supplier", back_populates="products")

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

                return products_data
            except Exception as ex:
                raise

    @classmethod
    def filter_product(cls, variant_id):
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
                        "factor_ponderador": price_list.value / last_net_cost['costo_neto'] if last_net_cost['costo_neto'] != None else "Indefinido",
                        "factor_ponderador_formated": format_decimal(price_list.value / last_net_cost['costo_neto']) if last_net_cost['costo_neto'] != None else "Indefinido"
                    })

                df_precios = pd.DataFrame(data_precios)
                if df_precios.empty:
                    price_list = []
                else:
                    price_list = df_precios.to_dict('records')

                product_data = {
                    **product.__dict__,
                    "stock": stock,
                    "reception_details_list": reception_details_list,
                    "consumption_details_list": consumption_details_list,
                    "sales_list": sales_list,
                    "last_net_cost": last_net_cost,
                    "price_list": price_list
                }
                
                return product_data  # Return the product's attributes directly
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
        
