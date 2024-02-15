from sqlalchemy import Column, Integer, String
from databases.base import Base
from databases.session import AppSession

class Office(Base):
    __tablename__ = 'officinas'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    municipality = Column(String(255))
    city = Column(String(255))
    country = Column(String(255))
    active_state = Column(String(255)) # CAMBIAR A NUM
    latitude = Column(String(255))
    longitude = Column(String(255))

    @classmethod
    def get_all_offices(cls):
        with AppSession() as session:
            try:
                offices = session.query(cls).all()
                office_data = [
                    {
                        key: value
                        for key, value in office.__dict__.items()
                        if not key.startswith('_')
                    } 
                    for office in offices
                ]
                return office_data
            except Exception as ex:
                raise
