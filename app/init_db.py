from databases.base import Base
from databases.session import app_engine

from models.user import User, Role
from models.cart import BuyCart, BuyCartDetail
from models.productos import Product, ProductStock
from models.document import Document, DocumentDetail
from models.reception import Reception, ReceptionDetail
from models.consumption import Consumption, ConsumptionDetail
from models.returns import Return
from models.sales import Sale, SaleDocument

Base.metadata.create_all(app_engine)



