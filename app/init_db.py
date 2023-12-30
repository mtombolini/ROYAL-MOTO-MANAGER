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

Base.metadata.create_all(app_engine)

with AppSession() as session:
    roles = [
        Role(id_role=0, description="desarrollador"),
        Role(id_role=1, description="administrador"),
        Role(id_role=2, description="invitado")
    ]

    for role in roles:
        session.merge(role)

    superadmin = User(
        username="superadmin",
        password="admin",
        nombre="Super",
        apellido="Admin",
        correo="superadmin@example.com",
        id_role=0
    )

    session.merge(superadmin)

    session.commit()

