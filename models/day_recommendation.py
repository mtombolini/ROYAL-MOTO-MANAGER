from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class DayRecommendation(Base):
    __tablename__ = 'recomendaciones_del_dia'

    variant_id = Column(Integer, ForeignKey('productos.variant_id'), primary_key=True)
    recommendation = Column(Integer)
    date = Column(DateTime)

    product = relationship("Product", back_populates="day_recommendation")

    @classmethod
    def get_all(cls):
        with AppSession() as session:
            try:
                recomendations = session.query(cls).all()

                recomendation_data = []
                for recomendation in recomendations:
                    recomendation_data.append({
                        'variant_id': recomendation.variant_id,
                        'sku': recomendation.product.sku,
                        'proveedor': recomendation.product.supplier.trading_name,
                        'description': recomendation.product.description,
                        'recommendation': recomendation.recommendation,
                        'date': recomendation.date
                    })

                sorted_data = sorted(recomendation_data, key=lambda x: (x['proveedor'], -x['recommendation']))
                
                return sorted_data
            except Exception as ex:
                raise