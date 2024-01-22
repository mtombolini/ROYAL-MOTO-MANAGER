from sqlalchemy import Column, Integer, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
from models.employee import EmployeeNotFoundError, EmployeeAttributeNotFoundError
from typing import List, Dict

class OvertimeRecordRecordNotFoundError(ValueError):
    """Exception raised when the overtime hours record of an employee 
    in a certain month is not found.""" 
    
class OvertimeRecordRecordAttributeNotFoundError(AttributeError):
    """Exception raised when trying to access an inexistent record attribute.""" 
    
class OvertimeRecordKeyError(KeyError):
    """Exception raised when the necessary keys/identifiers for a new record
    are not provided."""  

class OvertimeRecord(Base):
    __tablename__ = 'horas extra'

    employee_id = Column(Integer, ForeignKey('empleados.id'), primary_key=True)
    employee = relationship('Employee', back_populates='overtime_hours')
    month = Column(Date(), primary_key=True)
    overtime_hours = Column(Integer)

    @classmethod
    def get_all(cls) -> List[Dict]:
        with AppSession() as session:
            try:
                employees: List[cls] = session.query(cls).all()
                
                # Iterate through all attributes of each Employee object
                overtime_hours_data = [
                    {
                        key: value 
                        for key, value 
                        in record.__dict__.items() 
                        if not key.startswith('_')
                    }
                    for record in overtime_hours_data
                ]
                return overtime_hours_data
            except Exception as ex:
                # Undo any changes made to session
                raise
            
            
    @classmethod
    def get(cls, employee_id: int, month: str) -> Dict:
        with AppSession() as session:
            try:
                record = session.query(cls).filter(cls.id == employee_id,
                                                   cls.month == month).one_or_none()
                if record:
                    record_data = {
                        key: value 
                        for key, value 
                        in record.__dict__.items() 
                        if not key.startswith('_')
                    }
                    return record_data
                else:
                    raise OvertimeRecordRecordNotFoundError(
                        f'Overtime record of employee with ID {employee_id} on {month} not found.'
                    )
            except Exception as ex:
                raise
            
            
    @classmethod
    def create(cls, **kwargs) -> None:
        # Start a new session
        with AppSession() as session:
            try:
                # Create an instance of the class with the given kwargs
                new_record = cls()

                # Ensure composite key fields are present
                required_keys = ['employee_id', 'month']
                if not all(key in kwargs for key in required_keys):
                    missing_keys = ', '.join(key for key in required_keys if key not in kwargs)
                    raise KeyError(f'Missing required key(s): {missing_keys}')

                # Iterate over the kwargs and set them on the instance if they are valid attributes
                for key, value in kwargs.items():
                    if hasattr(new_record, key):
                        setattr(new_record, key, value)
                    else:
                        raise OvertimeRecordRecordAttributeNotFoundError(
                            f'Attribute {key} not found in overtime hours record'
                        )
                # Add the instance to the session
                session.add(new_record)
                # Commit the changes
                session.commit()
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def edit(cls, employee_id: int, month: str, **kwargs) -> None:
        # Start a new session
        with AppSession() as session:
            try:
                record_to_edit = session.query(cls).filter(cls.id == employee_id,
                                                           cls.month == month).one_or_none()
                for key, value in kwargs.items():
                    if hasattr(record_to_edit, key):
                        setattr(record_to_edit, key, value)
                    else:
                        raise OvertimeRecordRecordAttributeNotFoundError(
                            f'Attribute {key} not found in overtime hours record'
                        )
                # Commit the changes
                session.commit()
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def delete(cls, employee_id: int, month: str) -> None:
        with AppSession() as session:
            try:
                # Find the employee object to delete
                record_to_delete = session.query(cls).filter(cls.id == employee_id,
                                                             cls.month == month).one_or_none()
                # If it exists, delete it
                # Return bool indicating if the operation was successful
                if record_to_delete:
                    session.delete(record_to_delete)
                    session.commit()
                else:
                    raise OvertimeRecordRecordNotFoundError(
                        f'Overtime record of employee with ID {employee_id} on {month} not found.'
                    )
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise           
