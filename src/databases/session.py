from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Usar configuraciones para la conexión a la BD
DATABASE_CONFIG = config['development_postgres']
# APP_DB_URL_MYSQL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB}"
APP_DB_URL_POSTGRES = f"postgresql://{DATABASE_CONFIG.POSTGRES_USER}:{DATABASE_CONFIG.POSTGRES_PASSWORD}@{DATABASE_CONFIG.POSTGRES_HOST}/{DATABASE_CONFIG.POSTGRES_DB}"

app_engine = create_engine(APP_DB_URL_POSTGRES)
AppSession = sessionmaker(bind=app_engine)

