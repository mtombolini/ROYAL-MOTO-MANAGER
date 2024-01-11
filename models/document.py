from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from databases.base import Base

from models.sales import SaleDocument

class Document(Base):
    __tablename__ = 'documentos'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)  # Usamos DateTime en lugar de String
    # document_number = Column(String(255))
    # office = Column(String(255))
    total_amount = Column(Float)
    net_amount = Column(Float)
    document_type = Column(String(255))

    details = relationship("DocumentDetail", back_populates="document")
    sales = relationship("SaleDocument", back_populates="document")

class DocumentDetail(Base):
    __tablename__ = 'documentos_detalle'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documentos.id'))
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))  # Asumiendo que 'productos' es la tabla correcta
    quantity = Column(Integer)
    net_unit_value = Column(Float)
    net_total_value = Column(Float)

    document = relationship("Document", back_populates="details")
    product = relationship("Product", back_populates="document_details")


