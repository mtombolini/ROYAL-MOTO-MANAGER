from functools import wraps
from flask_login import current_user
from sqlalchemy.orm import joinedload
from databases.session import AppSession
from flask import render_template, redirect, url_for

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            from models.user import User, Role
            session = AppSession()

            try:
                user_with_role = session.query(User).options(joinedload(User.role)).filter_by(id=current_user.id).one_or_none()
                superadmin_id = session.query(Role).filter_by(description="superadministrador").first().id_role
                if not user_with_role or user_with_role.role.description not in roles and user_with_role.id_role != superadmin_id:
                    return render_template('alerta_permisos_usuarios.html')

                return f(*args, **kwargs)
            finally:
                session.close()
        return wrapped
    return wrapper