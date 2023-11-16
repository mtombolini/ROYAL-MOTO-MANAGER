from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from databases.base import CartsBase

class BuyCart(CartsBase):
    __tablename__ = 'carros_compras'

    cart_id = Column(Integer, primary_key=True)
    descripcion = Column(String(255))
    fecha_creacion = Column(DateTime)
    proveedor = Column(String(255))
    monto_neto = Column(Integer)  
    cantidad_productos = Column(Integer)
    estado = Column(String(255))
    revision = Column(String(255))
    rendimiento = Column(String(255))

    # Relación uno a muchos: un carro puede tener muchos detalles.
    details = relationship("BuyCartDetail", back_populates="cart")


class BuyCartDetail(CartsBase):
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

