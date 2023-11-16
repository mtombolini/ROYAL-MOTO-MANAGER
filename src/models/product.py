from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import ProductBase

class ProductDescription(ProductBase):
    __tablename__ = 'productos_descripcion'

    variant_id = Column(Integer, primary_key=True)
    tipo = Column(String(255))
    descripcion = Column(String(255))
    sku = Column(String(255))
    
    stock = relationship("ProductStock", uselist=False, back_populates="description")

    def __init__(self, variant_id="", sku="", tipo="", descripcion=""):
        self.variant_id = variant_id
        self.sku = sku
        self.tipo = tipo
        self.descripcion = descripcion

class ProductStock(ProductBase):
    __tablename__ = 'productos_stock'

    variant_id = Column(Integer, ForeignKey('productos_descripcion.variant_id'), primary_key=True)
    stock_lira = Column(Integer)
    stock_sobrexistencia = Column(Integer)
    
    description = relationship("ProductDescription", back_populates="stock")

    def __init__(self, variant_id="", stock_lira="", stock_sobrexistencia=""):
        self.variant_id = variant_id
        self.stock_lira = stock_lira
        self.stock_sobrexistencia = stock_sobrexistencia
