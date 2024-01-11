from models.tablas.employee import Employee
from databases.session import AppSession

class ModelEmployee:

    @classmethod
    def create(cls, username, rut, nombre, apellido, fecha_incorporacion, horario_colacion):
        session = AppSession()
        try:
            # Crea un nuevo empleado
            new_employee = Employee(username=username, rut=rut, nombre=nombre, apellido=apellido, fecha_incorporacion=fecha_incorporacion, horario_colacion=horario_colacion)
            
            # Agrega el nuevo empleado a la sesión de SQLAlchemy y realiza la inserción en la base de datos
            session.add(new_employee)
            session.commit()
            
            print(f"Empleado creado: Username={new_employee.username}, Rut={new_employee.rut}, Nombre={new_employee.nombre}, Apellido={new_employee.apellido}")

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

        
        
    
