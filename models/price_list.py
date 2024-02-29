from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class PriceList(Base):
    __tablename__ = 'lista_precios'

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer)
    name = Column(String)
    detail_id = Column(Integer)
    value = Column(Float)
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))
    
    product = relationship("Product", back_populates="price_list")

    @classmethod
    def get_price_list_by_variant_id(cls, variant_id):
        session = AppSession()
        try:
            price_list = session.query(PriceList).filter(PriceList.variant_id == variant_id).all()
            return price_list
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()