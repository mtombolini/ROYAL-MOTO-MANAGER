from models.tablas.employee import Employee
from databases.session import AppSession

class ModelEmployee:

    @classmethod
    def create(cls, user_id, rut, nombre, apellido, fecha_incorporacion, horario_colacion):
        session = AppSession()
        try:
            new_employee = Employee(user_id=user_id, rut=rut, nombre=nombre, apellido=apellido, fecha_incorporacion=fecha_incorporacion, horario_colacion=horario_colacion)
            session.add(new_employee)
            session.commit()
            return new_employee
        except Exception as ex:
            session.rollback()
            raise ex

        
    @classmethod
    def get_all_employees(cls):
        session = AppSession()
        try:
            employees = session.query(Employee).all()
            return employees
        except Exception as ex:
            raise ex
        finally:
            session.close()

        
        
    
