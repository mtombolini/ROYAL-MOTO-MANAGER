from sqlalchemy import Table, Column, Integer, ForeignKey, String
from databases.base import Base

product_supplier_association = Table('product_supplier_association', Base.metadata,
    Column('product_sku', String(255), ForeignKey('productos.sku')),
    Column('supplier_rut', String(12), ForeignKey('suppliers.rut'))
)