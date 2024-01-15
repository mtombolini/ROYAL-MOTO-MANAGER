from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from databases.base import Base

class PriceList(Base):
    __tablename__ = 'lista_precios'

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer)
    name = Column(String)
    detail_id = Column(Integer)
    value = Column(Float)
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))
    
    product = relationship("Product", back_populates="price_list")