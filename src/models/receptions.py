from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from databases.base import DocumentBase

class Reception(DocumentBase):
    __tablename__ = 'recepciones_general'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date)  # Usar Date o DateTime para fechas.
    documento = Column(String(255))
    nota = Column(String(255))

    # Agregar cascada a la relación
    details = relationship('ReceptionDetail', back_populates='reception', cascade="all, delete, delete-orphan")  # Relación con ReceptionDetail.

    def __init__(self, id="", fecha="", documento="", nota=""):
        self.id = id
        self.fecha = fecha
        self.documento = documento
        self.nota = nota

class ReceptionDetail(DocumentBase):
    __tablename__ = 'recepciones_detalle'

    id = Column(Integer, primary_key=True)  # Añadir una columna de ID.
    reception_id = Column(Integer, ForeignKey('recepciones_general.id', ondelete='CASCADE'), nullable=False)  # Agregar ondelete='CASCADE'
    cantidad = Column(Float)
    costo_neto = Column(Float)
    variant_id = Column(String(255))

    reception = relationship('Reception', back_populates='details')
