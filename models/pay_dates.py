from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession

class PayDates(Base):
    __tablename__ = 'fechas_pago'

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey('carros_compras.cart_id'))
    fecha_pago = Column(DateTime)

    # Relación muchos a uno: muchas fechas de pago pertenecen a un carro.
    cart = relationship("BuyCart", back_populates="pay_dates")

    @classmethod
    def get_pay_dates(cls, cart_id):
        session = AppSession()
        try:
            pay_dates = session.query(cls).filter(cls.cart_id == cart_id).all()
            return pay_dates
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def delete_existing_dates(cls, cart_id):
        session = AppSession()
        try:
            session.query(cls).filter(cls.cart_id == cart_id).delete()
            session.commit()
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def create_new_dates(cls, cart_id, dates):
        session = AppSession()
        try:
            result = session.execute(text("SELECT MAX(id) FROM fechas_pago"))
            max_id = result.scalar()
            suma = 0
            for date_str in dates:
                new_date = cls(id=max_id + 1 + suma, cart_id=cart_id, fecha_pago=datetime.strptime(date_str, '%Y-%m-%d'))
                session.add(new_date)
                suma += 1
            session.commit()
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()