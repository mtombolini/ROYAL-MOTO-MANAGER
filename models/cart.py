from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from databases.base import Base
from models.pay_dates import PayDates

class BuyCart(Base):
    __tablename__ = 'carros_compras'

    cart_id = Column(Integer, primary_key=True)
    descripcion = Column(String(255))
    fecha_creacion = Column(DateTime)
    fecha_recepcion = Column(DateTime)
    proveedor = Column(String(255))
    rut = Column(String(255))
    razon_social = Column(String(255))
    monto_neto = Column(Integer)  
    cantidad_productos = Column(Integer)
    estado = Column(String(255))
    revision = Column(String(255))
    rendimiento = Column(String(255))

    # Relación uno a muchos: un carro puede tener muchos detalles.
    details = relationship("BuyCartDetail", back_populates="cart")
    pay_dates = relationship("PayDates", back_populates="cart")


class BuyCartDetail(Base):
    __tablename__ = 'carros_compras_detalles'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carros_compras.cart_id'))
    variant_id = Column(Integer)
    descripcion_producto = Column(String(500))
    sku_producto = Column(String(255))
    costo_neto = Column(Float)  
    cantidad = Column(Integer)

    # Relación muchos a uno: muchos detalles pertenecen a un carro.
    cart = relationship("BuyCart", back_populates="details")