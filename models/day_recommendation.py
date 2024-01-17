from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class DayRecommendation(Base):
    __tablename__ = 'recomendaciones_del_dia'

    variant_id = Column(Integer, ForeignKey('productos.variant_id'), primary_key=True)
    recommendation = Column(Integer)
    date = Column(DateTime)

    product = relationship("Product", back_populates="day_recommendation")