from sqlalchemy import Column, Integer, DateTime, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class Consumption(Base):
    __tablename__ = 'consumos'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    office = Column(String(255))
    note = Column(String(255))

    details = relationship("ConsumptionDetail", back_populates="consumption")

class ConsumptionDetail(Base):
    __tablename__ = 'consumos_detalle'

    id = Column(Integer, primary_key=True)
    consumption_id = Column(Integer, ForeignKey('consumos.id'))
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))  # Asegúrate que esta sea la tabla y columna correctas
    quantity = Column(Integer)
    net_cost = Column(Float)  # Por ejemplo, 10 dígitos en total, 2 decimales.

    consumption = relationship("Consumption", back_populates="details")
    product = relationship("Product", back_populates="consumption_details")  
