from models.user import User, Role
from databases.session import AppSession

class ModelUser:

    @classmethod
    def login(cls, username, password):
        session = AppSession()
        try:
            user = session.query(User).join(Role).filter(User.username == username).one_or_none()
            if not user:
                return None
            if user.check_password(password):
                return user
            else:
                return False
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()


    @classmethod
    def register(cls, username, password, correo, nombre, apellido, id_role):
        session = AppSession()
        try:
            existing_user = session.query(User).filter(User.username == username).one_or_none()
            if existing_user:
                return None, session

            new_user = User(username=username, password=password, correo=correo, nombre=nombre, apellido=apellido, id_role=id_role)
            session.add(new_user)
            session.commit()

            return new_user, session
        except Exception as ex:
            session.rollback()
            raise Exception(ex)


    @classmethod
    def get_by_id(cls, user_id):
        session = AppSession()
        try:
            user = session.query(User).join(Role).filter(User.id == user_id).one_or_none()
            return user
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()


    @classmethod
    def get_all_roles(cls):
        session = AppSession()
        try:
            # Consulta los roles
            roles = session.query(Role).all()
            roles_with_users = []

            for role in roles:
                # Obtener los usuarios asociados a cada rol
                users = session.query(User.username).filter(User.id_role == role.id_role).all()
                usernames = [user.username for user in users]

                role_info = {
                    'id_role': role.id_role,
                    'description': role.description,
                    'usernames': usernames  # Lista de nombres de usuario asociados a este rol
                }
                roles_with_users.append(role_info)

            return roles_with_users

        except Exception as ex:
            raise Exception(ex)

        finally:
            session.close()


    @classmethod
    def get_all_users(cls):
        session = AppSession()
        try:
            # Consulta los usuarios
            users = session.query(User).all()
            return users

        except Exception as ex:
            raise Exception(ex)

        finally:
            session.close()


    @classmethod
    def get_role_by_id(cls, id_role):
        session = AppSession()
        try:
            role = session.query(Role).filter(Role.id_role == id_role).one_or_none()
            if role:
                # Crear y devolver un diccionario con la información del rol
                role_info = {
                    'id_role': role.id_role,
                    'description': role.description
                }
                return role_info, session
            else:
                return None, session
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()


    @classmethod
    def new_role(cls, description):
        session = AppSession()
        try:
            existing_role = session.query(Role).filter(Role.description == description).one_or_none()
            if existing_role:
                return None, session

            new_role = Role(description=description)
            session.add(new_role)
            session.commit()

            return new_role, session
        
        except Exception as ex:
            session.rollback()
            raise Exception(ex)
        
        
    @classmethod
    def delete_role(cls, id_role):
        session = AppSession()
        try:
            # Buscar el rol por su ID
            role_to_delete = session.query(Role).filter(Role.id_role == id_role).one_or_none()
            
            if role_to_delete == 1:
                return False, session
                
            # Si el rol existe, eliminarlo
            if role_to_delete:
                session.delete(role_to_delete)
                session.commit()
                return True, session
            else:
                return False, session

        except Exception as ex:
            session.rollback()  # Revertir los cambios en caso de excepción
            raise Exception(ex)
        finally:
            session.close()  # Cerrar la sesión en cualquier caso
            
            
    @classmethod
    def edit_role(cls, id_role, new_description):
        session = AppSession()
        try:
            # Buscar el rol por su ID
            role_to_edit = session.query(Role).filter(Role.id_role == id_role).one_or_none()

            # Si el rol existe, actualizar su descripción
            if role_to_edit:
                role_to_edit.description = new_description
                session.commit()
                return True, session
            else:
                return False, session

        except Exception as ex:
            session.rollback()  # Revertir los cambios en caso de excepción
            raise Exception(ex)
        finally:
            session.close()  # Cerrar la sesión en cualquier caso
            
            
    @classmethod
    def delete_user(cls, id_user):
        session = AppSession()
        try:
            # Buscar el user por su ID
            user_to_delete = session.query(User).filter(User.id == id_user).one_or_none()
                
            # Si el rol existe, eliminarlo
            if user_to_delete:
                session.delete(user_to_delete)
                session.commit()
                return True, session
            else:
                return False, session

        except Exception as ex:
            session.rollback()  # Revertir los cambios en caso de excepción
            raise Exception(ex)
        finally:
            session.close()  # Cerrar la sesión en cualquier caso


    @classmethod
    def edit_user(cls, user_id, username, correo, nombre, apellido, id_role):
        session = AppSession()
        try:
            user_to_edit = session.query(User).filter(User.id == user_id).one_or_none()
            if user_to_edit:
                user_to_edit.username = username
                user_to_edit.correo = correo
                user_to_edit.nombre = nombre
                user_to_edit.apellido = apellido
                user_to_edit.id_role = id_role
                session.commit()
                return True, session
            else:
                return False, session
        except Exception as ex:
            session.rollback()
            raise Exception(ex)
        finally:
            session.close()
            
    
    @classmethod
    def is_superadmin(cls, id_role):
        session = AppSession()
        try:
            current_role, _ = cls.get_role_by_id(id_role)
            return current_role.description.lower() == 'superadministrador', session
        except Exception as ex:
            session.rollback()
            raise Exception(ex)
        finally:
            session.close()
            
            
    @classmethod
    def is_user_the_superadmin(cls, id_user):
        session = AppSession()
        try:
            user_id_role = session.query(User.id_role).filter(User.id == id_user).one_or_none().id_role()
            return cls.is_superadmin(user_id_role)
        except Exception as ex:
            session.rollback()
            raise Exception(ex)
        finally:
            session.close()
            

    @classmethod
    def role_has_associated_users(cls, id_role):
        session = AppSession()
        try:
            roles_with_users = cls.get_all_roles()
            for role in roles_with_users:
                if role.id_role == id_role:
                    return len(role.usernames) > 0, session
        except Exception as ex:
            session.rollback()
            raise Exception(ex)
        finally:
            session.close()
