from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, drop_database, database_exists
from sqlalchemy.exc import ProgrammingError
from app.config import config

DATABASE_CONFIG = config['production']
APP_DB_URL = DATABASE_CONFIG.DATA_BASE_URL
DEFAULT_DB_URL = DATABASE_CONFIG.DEFAULT_DATABASE_URL

def create_db(db_url, default_db_url):
    default_engine = create_engine(default_db_url)
    
    try:
        existe = database_exists(db_url)

    except UnicodeDecodeError as e:
        existe = False

    if not existe:
        create_database(db_url)
    
    default_engine.dispose()
    
    return create_engine(db_url)

app_engine = create_db(APP_DB_URL, DEFAULT_DB_URL)
AppSession = sessionmaker(bind=app_engine)

