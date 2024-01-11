from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
import pandas as pd

from models.consumption import ConsumptionDetail
from models.reception import ReceptionDetail
from models.document import DocumentDetail

class Product(Base):
    __tablename__ = 'productos'

    variant_id = Column(Integer, primary_key=True)
    type = Column(String(255))
    description = Column(String(255))
    sku = Column(String(255))
    
    # asegúrate de que 'stock' corresponda al nombre de la relación inversa en ProductStock
    stock = relationship("ProductStock", uselist=False, back_populates="product")
    consumption_details = relationship("ConsumptionDetail", back_populates="product")
    reception_details = relationship("ReceptionDetail", back_populates="product")
    document_details = relationship("DocumentDetail", back_populates="product")

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
                
                reception = [
                    {
                        key: value 
                        for key, value in reception_detail.reception.__dict__.items() 
                        if not key.startswith('_')
                    }
                for reception_detail in product.reception_details
                ]

                reception_details = [
                    {
                        key: value 
                        for key, value in reception_detail.__dict__.items() 
                        if not key.startswith('_')
                    }
                for reception_detail in product.reception_details
                ]

                consumptions = [
                    {
                        key: value 
                        for key, value in consumption_detail.consumption.__dict__.items() 
                        if not key.startswith('_')
                    }
                for consumption_detail in product.consumption_details
                ]

                consumption_details = [
                    {
                        key: value 
                        for key, value in consumption_detail.__dict__.items() 
                        if not key.startswith('_')
                    }
                for consumption_detail in product.consumption_details
                ]

                document_details = [
                    {
                        key: value 
                        for key, value in document_detail.__dict__.items() 
                        if not key.startswith('_')
                    }
                for document_detail in product.document_details
                ]

                documents = [document_detail.document for document_detail in product.document_details]

                documentos = []
                sales = []
                sales_docs = []
                for document in documents:
                    if document.sales != []:
                        documentos.append(document.__dict__)
                        for sale in document.sales:
                            sales_docs.append(sale.__dict__)
                            sales.append(sale.sale.__dict__)

                data = []
                for reception_detail in product.reception_details:
                    reception = reception_detail.reception
                    data.append({
                        "fecha": reception.date,
                        "tipo_de_documento": reception.document_type,
                        #"numero_de_documento": reception.document_number,
                        "nota": reception.note,
                        "cantidad": reception_detail.quantity,
                        "costo_neto": reception_detail.net_cost
                    })

                df = pd.DataFrame(data)
                reception_details_list = df.sort_values('fecha').to_dict('records')

                data_consumos = []
                for consumption_detail in product.consumption_details:
                    consumption = consumption_detail.consumption
                    data_consumos.append({
                        "fecha": consumption.date,
                        "nota": consumption.note,
                        "cantidad": consumption_detail.quantity,
                        "costo_neto": consumption_detail.net_cost
                    })

                df_consumos = pd.DataFrame(data_consumos)
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
                                "tipo_de_documento": document.document_type,
                                #"numero_de_documento": document.document_number,
                                "cantidad": document_detail.quantity,
                                "valor_unitario": document_detail.net_total_value,
                                "valor_total": document_detail.net_total_value * document_detail.quantity
                            })

                df_ventas = pd.DataFrame(data_ventas)
                sales_list = df_ventas.drop_duplicates().sort_values('fecha').to_dict('records')
                    
                product_data = {
                    **product.__dict__,
                    "stock": stock,
                    "reception": reception,
                    "reception_details": reception_details,
                    "consumptions": consumptions,
                    "consumption_details": consumption_details,
                    "documents": documentos,
                    "document_details": document_details,
                    "sales": sales,
                    "sales_docs": sales_docs,
                    "reception_details_list": reception_details_list,
                    "consumption_details_list": consumption_details_list,
                    "sales_list": sales_list
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
        
