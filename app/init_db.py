from databases.base import Base
from databases.session import app_engine, AppSession

from models.returns import Return
from models.user import User, Role
from models.supplier import Supplier
from models.shipping import Shipping
from models.price_list import PriceList
from models.sales import Sale, SaleDocument
from models.cart import BuyCart, BuyCartDetail
from models.productos import Product, ProductStock
from models.document import Document, DocumentDetail
from models.day_recommendation import DayRecommendation
from models.reception import Reception, ReceptionDetail
from models.consumption import Consumption, ConsumptionDetail
from models.employee import Employee
from models.overtime_hours import OvertimeRecord
from models.last_net_cost import LastNetCost

from sqlalchemy import func

class InitDB():
    def __init__(self):
        pass

    def create_data_base(self):
        Base.metadata.create_all(app_engine)

    def initialize_database(self):
        with AppSession() as session:
            self.create_init_data(session)
    
    def create_roles(self, session):
        roles = [
            Role(description="superadministrador"),
            Role(description="desarrollador"),
            Role(description="administrador"),
            Role(description="invitado")
        ]

        for role in roles:
            session.merge(role)

    def create_superadmin(self, session):
        superadmin_id = session.query(Role).filter_by(description="superadministrador").first().id_role

        superadmin = User(
            username="superadmin",
            password="admin",
            nombre="Super",
            apellido="Admin",
            correo="superadmin@example.com",
            id_role=superadmin_id,
        )

        session.merge(superadmin)

    def create_init_data(self, session):
        roles_count = session.query(func.count(Role.id_role)).scalar()
        if roles_count == 0:
            self.create_roles(session)
            self.create_superadmin(session)

            session.commit()
        else:
            print("Roles ya inicializados.")

    def main(self):
        self.create_data_base()
        self.initialize_database()
        
if __name__ == '__main__':
    init_db = InitDB()
    init_db.main()