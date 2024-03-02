from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class LastNetCost(Base):
    __tablename__ = 'last_net_cost'

    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey('productos.variant_id'))
    net_cost_formated = Column(String(255))
    net_cost = Column(Float)
    date = Column(DateTime)

    product = relationship("Product", back_populates="last_net_cost")

    @classmethod
    def create_last_net_cost(cls, variant_id, net_cost_formated, net_cost, date):
        with AppSession() as session:
            try:
                last_net_cost = cls(
                    variant_id=variant_id, 
                    net_cost_formated=net_cost_formated, 
                    net_cost=net_cost, 
                    date=date)

                session.add(last_net_cost)
                session.commit()
            
                return last_net_cost
            except Exception as ex:
                raise
            finally:
                session.close()