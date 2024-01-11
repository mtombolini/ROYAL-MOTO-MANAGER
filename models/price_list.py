from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from databases.base import Base

class PriceList(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True)
    detail_id = Column(Integer)
    value = Column(Float)
    variant_id = Column(Integer)
    
    # asegúrate de que 'stock' corresponda al nombre de la relación inversa en ProductStock
    product = relationship("Product", back_populates="price_list")