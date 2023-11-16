from .user import User, Role
from databases.session import UserSession

class ModelUser:

    @classmethod
    def login(cls, username, password):
        session = UserSession()
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
    def get_by_id(cls, user_id):
        session = UserSession()
        try:
            user = session.query(User).join(Role).filter(User.id == user_id).one_or_none()  
            return user
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def get_all_sellers(cls):
        session = UserSession()
        try:
            vendedores = session.query(User).filter(User.id_role == 2).all()
            return vendedores
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

