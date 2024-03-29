from sqlalchemy import Column, Integer, String, Select, text, ForeignKey
from sqlalchemy.types import Enum
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
from typing import List, Dict
import enum
from models.associations import product_supplier_association


class SupplierNotFoundError(ValueError):
    """Exception raised when a supplier is not found."""
    
class SupplierAttributeNotFoundError(AttributeError):
    """Exception raised when trying to access an inexistent supplier attribute."""

class CreditTerm(enum.Enum):
    THIRTY_DAYS = '30 Días'
    SIXTY_DAYS = '60 Días'
    ONE_TWENTY_DAYS = '120 Días'
    RETURN = 'Devolución'

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String(12), unique=True)
    business_name = Column(String(255))
    trading_name = Column(String(255))
    credit_term = Column(Enum(CreditTerm))
    delivery_period = Column(Integer)

    products = relationship('Product', secondary=product_supplier_association, back_populates='suppliers')

    @classmethod
    def create_from_df(cls, supplier_df):
        with AppSession() as session:
            try:
                for index, row in supplier_df.iterrows():
                    existing_supplier = session.query(cls).filter_by(rut=row['rut']).first()
                    if existing_supplier:
                        existing_supplier.business_name = row['business_name']
                        existing_supplier.trading_name = row['trading_name']
                        existing_supplier.credit_term = row['credit_term']
                        existing_supplier.delivery_period = row['delivery_period']
                    else:
                        result = session.execute(text("SELECT MAX(id) FROM suppliers"))
                        max_id = result.scalar()
                        new_supplier = cls(
                            id=max_id + 1,
                            rut=row['rut'],
                            business_name=row['business_name'],
                            trading_name=row['trading_name'],
                            credit_term=row['credit_term'],
                            delivery_period=row['delivery_period']
                        )
                        session.add(new_supplier)
                session.commit()
            except Exception as ex:
                session.rollback()
                raise

    @classmethod
    def get_all(cls) -> List[Dict]:
        session = AppSession()
        try:
            suppliers = session.query(cls).all()
            
            # Iterate through all attributes of each Supplier object
            suppliers_data = [
                {
                    key: value 
                    for key, value 
                    in supplier.__dict__.items() 
                    if not key.startswith('_')
                }
                for supplier in suppliers
            ]
            return suppliers_data
        except Exception as ex:
            # Undo any changes made to session
            raise
        finally:
            session.close()
            
            
    @classmethod
    def get(cls, supplier_id: int) -> Dict:
        with AppSession() as session:
            try:
                supplier = session.query(cls).filter(cls.id == supplier_id).one_or_none()
                if supplier:
                    supplier_data = {
                        key: value 
                        for key, value 
                        in supplier.__dict__.items() 
                        if not key.startswith('_')
                    }
                    return supplier_data
                else:
                    raise SupplierNotFoundError(f'Supplier with ID {supplier_id} not found.')
            except Exception as ex:
                raise
            
            
    @classmethod
    def create(cls, **kwargs) -> Dict:
        # Start a new session
        with AppSession() as session:
            try:
                # Create an instance of the class with the given kwargs
                new_supplier = cls()
                # Iterate over the kwargs and set them on the instance if they are valid attributes
                for key, value in kwargs.items():
                    if hasattr(new_supplier, key):
                        setattr(new_supplier, key, value)
                    else:
                        # Raise an exception if we try to edit an inexistent attribute
                        raise SupplierAttributeNotFoundError(
                            f'Attribute {key} not found in Supplier'
                        )
                # Add the instance to the session
                session.add(new_supplier)
                # Commit the changes
                session.commit()
                new_supplier_data = {
                    key: value 
                    for key, value 
                    in kwargs.items()
                }
                return new_supplier_data
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def edit(cls, supplier_id, **kwargs) -> Dict:
        # Start a new session
        with AppSession() as session:
            try:
                # Find the Supplier object to edit
                supplier_to_edit = session.query(cls).filter(cls.id == supplier_id).one_or_none()
                # Iterate over the kwargs and reset the values with them if they are valid attributes
                for key, value in kwargs.items():
                    if hasattr(supplier_to_edit, key):
                        setattr(supplier_to_edit, key, value)
                    else:
                        # Raise an exception if we try to edit an inexistent attribute
                        raise SupplierAttributeNotFoundError(
                            f'Attribute {key} not found in Supplier'
                        )
                # Commit the changes
                session.commit()
                edited_supplier_data = {
                    key: value 
                    for key, value 
                    in kwargs.items()
                }
                return edited_supplier_data
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def delete(cls, supplier_id: int) -> None:
        with AppSession() as session:
            try:
                # Find the Supplier object to delete
                supplier_to_delete = session.query(cls).filter(cls.id == supplier_id).one_or_none()
                # If it exists, delete it
                # Return bool indicating if the operation was successful
                if supplier_to_delete:
                    session.delete(supplier_to_delete)
                    session.commit()
                else:
                    raise SupplierNotFoundError(f'Supplier with ID {supplier_id} not found.')
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise

    @classmethod
    def get_all_class(cls) -> List[Dict]:
        session = AppSession()
        try:
            suppliers = session.query(cls).all()
            return suppliers
        except Exception as ex:
            # Undo any changes made to session
            raise
        finally:
            session.close()