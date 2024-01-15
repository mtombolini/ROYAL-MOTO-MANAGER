from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import relationship
from databases.base import Base

class Shipping(Base):
    __tablename__ = 'despachos'

    id = Column(Integer, primary_key=True)
    shipping_date = Column(DateTime)
    shipping_number = Column(String(255))
    shipping_type = Column(String(255))
    document_type = Column(String(255))
