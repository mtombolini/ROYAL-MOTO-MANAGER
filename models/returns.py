from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class Return(Base):
    __tablename__ = 'devoluciones'

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documentos.id'))  # Relación con la tabla de documentos
    credit_note_id = Column(Integer, ForeignKey('documentos.id'), nullable=True)  # Relación con la misma tabla de documentos

    # Define las relaciones. Asumiendo que 'Document' es tu clase de modelo para la tabla 'documentos'
    document = relationship("Document", foreign_keys=[document_id])
    credit_note = relationship("Document", foreign_keys=[credit_note_id])
