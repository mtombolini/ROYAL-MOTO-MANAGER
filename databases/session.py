from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import config

DATABASE_CONFIG = config['production']
APP_DB_URL = DATABASE_CONFIG.DATA_BASE_URL

app_engine = create_engine(APP_DB_URL)
AppSession = sessionmaker(bind=app_engine)

