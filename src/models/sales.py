from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class Sale(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    payment_type = Column(String(50))

    documents = relationship("SaleDocument", back_populates="sale")

class SaleDocument(Base):
    __tablename__ = 'ventas_documentos'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('ventas.id'))  # Establishes a foreign key relationship
    document_id = Column(Integer, ForeignKey('documentos.id'))  # Establishes a foreign key relationship

    # Relationships to the Sale and Document
    sale = relationship("Sale", back_populates="documents")
    document = relationship("Document", back_populates="sales")