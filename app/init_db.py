from databases.base import Base
from databases.session import app_engine, AppSession

from models.user import User, Role
from models.cart import BuyCart, BuyCartDetail
from models.productos import Product, ProductStock
from models.document import Document, DocumentDetail
from models.reception import Reception, ReceptionDetail
from models.consumption import Consumption, ConsumptionDetail
from models.returns import Return
from models.sales import Sale, SaleDocument
from models.price_list import PriceList
from models.supplier import Supplier
from models.shipping import Shipping

from sqlalchemy import func

Base.metadata.create_all(app_engine)

with AppSession() as session:
    # Check if roles exist
    roles_count = session.query(func.count(Role.id_role)).scalar()
    if roles_count == 0:
        roles = [
            Role(description="superadministrador"),
            Role(description="desarrollador"),
            Role(description="administrador"),
            Role(description="invitado")
        ]

        for role in roles:
            session.merge(role)
            
        superadmin_id = session.query(Role).filter_by(description="superadministrador").first().id_role

        superadmin = User(
            username="superadmin",
            password="admin",
            nombre="Super",
            apellido="Admin",
            correo="superadmin@example.com",
            id_role=superadmin_id, # 1
        )

        session.merge(superadmin)

        session.commit()

    else:
        print("Roles ya inicializados.")
