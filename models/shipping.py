from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class Shipping(Base):
    __tablename__ = 'despachos'

    id = Column(Integer, primary_key=True)
    shipping_date = Column(DateTime)
    shipping_number = Column(String(255))
    shipping_type = Column(String(255))
    document_type = Column(String(255))
    state = Column(Integer)

    @classmethod
    def get_all_shippings(cls):
        with AppSession() as session:
            try:
                shippings = session.query(cls).all()
                shippings_data = [
                    {
                        key: value 
                        for key, value in shipping.__dict__.items() 
                        if not key.startswith('_')
                    } 
                for shipping in shippings
                ]

                return shippings_data
            except Exception as ex:
                raise

    @classmethod
    def seach_shipping_guide_by_number(cls, guide_number):
        doc_type = "GUÍA DE DESPACHO ELECTRÓNICA T"
        with AppSession() as session:
            try:
                shipping = session.query(cls).filter(cls.shipping_number == guide_number).filter(cls.document_type == doc_type).first()

                if shipping is None:
                    return None
                
                else:
                    shipping_data = {
                        key: value 
                        for key, value in shipping.__dict__.items() 
                        if not key.startswith('_')
                    }

                return shipping_data
            except Exception as ex:
                raise