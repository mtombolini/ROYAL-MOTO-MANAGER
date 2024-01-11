from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class Reception(Base):
    __tablename__ = 'recepciones'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)  # Usamos DateTime en lugar de String
    document_type = Column(String(255))
    # document_number = Column(String(255))
    # office = Column(String(255))
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

    @classmethod
    def get_all_receptions_details(cls):
        with AppSession() as session:
            try:
                details = session.query(cls).all()
                details_data = [
                    {
                        key: value 
                        for key, value in detail.__dict__.items() 
                        if not key.startswith('_')
                    } 
                for detail in details
                ]

                return details_data
            except Exception as ex:
                raise

    @classmethod
    def filter_receptions_details_by_variant(cls, variant_id):
        with AppSession() as session:
            try:
                details = session.query(cls).filter(cls.variant_id == variant_id).all()
                details_data = [
                    {
                        key: value 
                        for key, value in detail.__dict__.items() 
                        if not key.startswith('_')
                    } 
                for detail in details
                ]

                return details_data
            except Exception as ex:
                raise