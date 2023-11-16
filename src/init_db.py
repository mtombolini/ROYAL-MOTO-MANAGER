from databases.base import UserBase, ProductBase, DocumentBase, CartsBase
from databases.session import user_engine
from databases.session import product_engine
from databases.session import document_engine
from databases.session import cart_engine

# BD: royal_manager_user
# from models.user import User, Role

# BD: royal_manager_products
from models.product import ProductDescription, ProductStock

# BD: royal_manager_documents
from models.receptions import Reception, ReceptionDetail

# BD: royal_manager_carts
from models.cart import BuyCart, BuyCartDetail

# UserBase.metadata.create_all(user_engine)
# ProductBase.metadata.create_all(product_engine)
# DocumentBase.metadata.create_all(document_engine)
CartsBase.metadata.create_all(cart_engine)



