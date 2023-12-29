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