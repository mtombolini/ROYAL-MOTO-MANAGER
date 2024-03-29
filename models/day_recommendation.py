from databases.base import Base
from databases.session import AppSession
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, cast, or_

class DayRecommendation(Base):
    __tablename__ = 'recomendaciones_del_dia'

    variant_id = Column(Integer, ForeignKey('productos.variant_id'), primary_key=True)
    recommendation = Column(Integer)
    date = Column(DateTime)

    product = relationship("Product", back_populates="day_recommendation")

    @classmethod
    def get_all(cls):
        from models.productos import Product
        with AppSession() as session:
            try:
                recomendations = session.query(cls).all()

                recomendation_data = []
                for recomendation in recomendations:
                    recomendation_data.append({
                        'variant_id': recomendation.variant_id,
                        'sku': recomendation.product.sku,
                        'proveedor': recomendation.product.suppliers[0].trading_name,
                        'rut': recomendation.product.suppliers[0].rut,
                        'description': recomendation.product.description,
                        'recommendation': recomendation.recommendation,
                        'date': recomendation.date,
                        'last_net_cost': recomendation.product.last_net_cost.net_cost
                    })
                

                sorted_data = sorted(recomendation_data, key=lambda x: (x['proveedor'], -x['recommendation']))
                
                return sorted_data
            except Exception as ex:
                raise

    @classmethod
    def filter_recommendations(cls, search_query):
        from models.productos import Product
        from models.supplier import Supplier
        with AppSession() as session:
            try:
                search_query = f"%{search_query.lower()}%"
                recommendations = session.query(cls).filter(
                    or_(
                        cast(cls.variant_id, String).ilike(search_query),
                        cls.product.has(Product.sku.ilike(search_query)),
                        cls.product.has(Product.description.ilike(search_query)),
                        cls.product.has(Product.suppliers.any(Supplier.trading_name.ilike(search_query)))
                    )
                ).all()

                recomendation_data = []
                for recomendation in recommendations:
                    recomendation_data.append({
                        'variant_id': recomendation.variant_id,
                        'sku': recomendation.product.sku,
                        'proveedor': recomendation.product.suppliers[0].trading_name,
                        'description': recomendation.product.description,
                        'recommendation': recomendation.recommendation,
                        'date': recomendation.date
                    })

                # sorted_data = sorted(recomendation_data, key=lambda x: (x['proveedor'], -x['recommendation']))

                return recomendation_data
            
            except Exception as ex:
                raise

