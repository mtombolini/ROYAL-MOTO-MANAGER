from functools import wraps
from flask import render_template, redirect, url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload

# Importa la UserSession desde tu módulo session
from databases.session import AppSession

def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))

            # Importación local de User
            from models.user import User

            # Iniciar una sesión
            session = AppSession()

            try:
                user_with_role = session.query(User).options(joinedload(User.role)).filter_by(id=current_user.id).one_or_none()

                if not user_with_role or user_with_role.role.description not in roles:
                    return render_template('alerta_permisos_usuarios.html')

                return f(*args, **kwargs)
            finally:
                session.close()  # Cierra la sesión después de utilizarla
        return wrapped
    return wrapper
