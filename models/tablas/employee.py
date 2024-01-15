from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class Employee(Base):
    __tablename__ = 'empleados'

    id = Column(Integer, primary_key=True)
    # Establecer una relación con el ID del usuario en la tabla 'usuarios'
    user_id = Column(Integer, ForeignKey('usuarios.id'))
    # Crear la relación con el modelo User, utilizando 'user' como el nombre de la relación
    user = relationship('User', back_populates='empleados')
    rut = Column(String(255))
    nombre = Column(String(255))
    apellido = Column(String(255))
    fecha_incorporacion = Column(String(255))
    horario_colacion = Column(String(255))  # Nombre de variable ajustado

