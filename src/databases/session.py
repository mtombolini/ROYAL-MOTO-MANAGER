from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Usar configuraciones para la conexión a la BD
DATABASE_CONFIG = config['development']

# USER_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB_USERS_CONNECTION}"
# PRODUCT_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB_PRODUCTS_CONNECTION}"
# DOCUMENTS_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB_DOCUMENTS_CONNECTION}"
# CARTS_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB_CARTS_CONNECTION}"

APP_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB}"

# user_engine = create_engine(USER_DB_URL)
# product_engine = create_engine(PRODUCT_DB_URL)
# document_engine = create_engine(DOCUMENTS_DB_URL)
# cart_engine = create_engine(CARTS_DB_URL)

app_engine = create_engine(APP_DB_URL)

# Crear factorías de sesiones de SQLAlchemy
# UserSession = sessionmaker(bind=user_engine)
# ProductSession = sessionmaker(bind=product_engine)
# DocumentSession = sessionmaker(bind=document_engine)
# CartSession = sessionmaker(bind=cart_engine)

AppSession = sessionmaker(bind=app_engine)

