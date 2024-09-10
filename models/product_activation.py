from sqlalchemy import Column, Integer, String, Boolean
from databases.base import Base
from databases.session import AppSession

class ProductActivation(Base):
    __tablename__ = 'product_activations'
    
    id = Column(Integer, primary_key=True)
    sku = Column(String(255), unique=True)
    is_active = Column(Boolean, default=True)

    @classmethod
    def get_product_activation_state(cls, sku):
        with AppSession() as session:
            try:
                product = session.query(cls).filter_by(sku=sku).first()
                return product.is_active
            except Exception as ex:
                print(ex)
                raise

    @classmethod
    def update_activation_state(cls, sku, state):
        with AppSession() as session:
            try:
                product = session.query(cls).filter_by(sku=sku).first()
                product.is_active = state
                session.commit()
            except Exception as ex:
                print(ex)
                session.rollback()
                raise
