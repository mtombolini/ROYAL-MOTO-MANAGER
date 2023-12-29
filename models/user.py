from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from databases.base import Base

class User(Base, UserMixin):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    _password = Column('password', String(255))
    nombre = Column(String(255))
    apellido = Column(String(255))
    correo = Column(String(255))
    id_role = Column(Integer, ForeignKey('roles.id_role'))
    role = relationship('Role', back_populates='users')

    def __init__(self, username="", password="", nombre="", apellido="", correo="", id_role=None):
        self.username = username
        self.password = password
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.id_role = id_role

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext_password):
        self._password = generate_password_hash(plaintext_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

class Role(Base):
    __tablename__ = 'roles'

    id_role = Column(Integer, primary_key=True)
    description = Column(String(255))
    users = relationship('User', back_populates='role')
