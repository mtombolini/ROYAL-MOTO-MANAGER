from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config

# Usar configuraciones para la conexión a la BD
DATABASE_CONFIG = config['development']
APP_DB_URL = f"mysql+mysqldb://{DATABASE_CONFIG.MYSQL_USER}:{DATABASE_CONFIG.MYSQL_PASSWORD}@{DATABASE_CONFIG.MYSQL_HOST}/{DATABASE_CONFIG.MYSQL_DB}"

app_engine = create_engine(APP_DB_URL)
AppSession = sessionmaker(bind=app_engine)

