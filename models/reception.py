from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from databases.base import Base

class Reception(Base):
    __tablename__ = 'recepciones'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)  # Usamos DateTime en lugar de String
    document_type = Column(String(255))
    note = Column(String(255))

    details = relationship("ReceptionDetail", back_populates="reception")

class ReceptionDetail(Base):
    __tablename__ = 'recepciones_detalle'

    id = Column(Integer, primary_key=True)
    reception_id = Column(Integer, ForeignKey('recepciones.id'))
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))  # Asumiendo que 'productos' es la tabla correcta
    quantity = Column(Integer)
    net_cost = Column(Float)

    reception = relationship("Reception", back_populates="details")
    product = relationship("Product", back_populates="reception_details")