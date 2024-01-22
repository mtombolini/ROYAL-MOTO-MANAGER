from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time
from sqlalchemy.orm import relationship
from databases.base import Base
from databases.session import AppSession
from typing import List, Dict

class EmployeeNotFoundError(ValueError):
    """Exception raised when an employee is not found."""
    
class EmployeeAttributeNotFoundError(AttributeError):
    """Exception raised when trying to access an inexistent employee attribute."""

class Employee(Base):
    __tablename__ = 'empleados'

    id = Column(Integer, primary_key=True)
    # Establecer una relación con el ID del usuario en la tabla 'usuarios'
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    # Crear la relación con el modelo User, utilizando 'user' como el nombre de la relación
    user = relationship('User', back_populates='employee')
    run = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    joined_in = Column(Date())
    lunch_break = Column(Time())  # Nombre de variable ajustado
    overtime_hours = relationship('OvertimeRecord', back_populates='employee')

    @classmethod
    def get_all(cls) -> List[Dict]:
        with AppSession() as session:
            try:
                employees: List[cls] = session.query(cls).all()
                
                # Iterate through all attributes of each Employee object
                employees_data = [
                    {
                        key: value 
                        for key, value 
                        in employee.__dict__.items() 
                        if not key.startswith('_')
                    }
                    for employee in employees
                ]
                return employees_data
            except Exception as ex:
                # Undo any changes made to session
                raise
            
            
    @classmethod
    def get(cls, employee_id: int) -> Dict:
        with AppSession() as session:
            try:
                employee = session.query(cls).filter(cls.id == employee_id).one_or_none()
                if employee:
                    employee_data = {
                        key: value 
                        for key, value 
                        in employee.__dict__.items() 
                        if not key.startswith('_')
                    }
                    return employee_data
                else:
                    raise EmployeeNotFoundError(f'employee with ID {employee_id} not found.')
            except Exception as ex:
                raise
            
            
    @classmethod
    def create(cls, **kwargs) -> None:
        # Start a new session
        with AppSession() as session:
            try:
                # Create an instance of the class with the given kwargs
                new_employee = cls()
                # Iterate over the kwargs and set them on the instance if they are valid attributes
                for key, value in kwargs.items():
                    if hasattr(new_employee, key):
                        setattr(new_employee, key, value)
                    else:
                        # Raise an exception if we try to edit an inexistent attribute
                        raise EmployeeAttributeNotFoundError(
                            f'Attribute {key} not found in employee'
                        )
                # Add the instance to the session
                session.add(new_employee)
                # Commit the changes
                session.commit()
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def edit(cls, employee_id, **kwargs) -> None:
        # Start a new session
        with AppSession() as session:
            try:
                # Find the employee object to edit
                employee_to_edit = session.query(cls).filter(cls.id == employee_id).one_or_none()
                # Iterate over the kwargs and reset the values with them if they are valid attributes
                for key, value in kwargs.items():
                    if hasattr(employee_to_edit, key):
                        setattr(employee_to_edit, key, value)
                    else:
                        # Raise an exception if we try to edit an inexistent attribute
                        raise EmployeeAttributeNotFoundError(
                            f'Attribute {key} not found in employee'
                        )
                # Commit the changes
                session.commit()
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise
            
            
    @classmethod
    def delete(cls, employee_id: int) -> None:
        with AppSession() as session:
            try:
                # Find the employee object to delete
                employee_to_delete = session.query(cls).filter(cls.id == employee_id).one_or_none()
                # If it exists, delete it
                # Return bool indicating if the operation was successful
                if employee_to_delete:
                    session.delete(employee_to_delete)
                    session.commit()
                else:
                    raise EmployeeNotFoundError(f'employee with ID {employee_id} not found.')
            except Exception as ex:
                # Undo any changes made to session
                session.rollback()
                raise           
