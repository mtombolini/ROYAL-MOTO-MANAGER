from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class PayDates(Base):
    __tablename__ = 'fechas_pago'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carros_compras.cart_id'))
    fecha_pago = Column(DateTime)

    # Relación muchos a uno: muchas fechas de pago pertenecen a un carro.
    cart = relationship("BuyCart", back_populates="pay_dates")