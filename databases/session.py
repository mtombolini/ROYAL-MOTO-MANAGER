from app.config import CONFIG

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

APP_DB_URL = CONFIG.DATABASE_URL
DEFAULT_DB_URL = CONFIG.DEFAULT_DATABASE_URL

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


if DATABASE_CONFIG == config['development_postgres']:
    app_engine = create_db(APP_DB_URL, DEFAULT_DB_URL)
else:
    app_engine = create_engine(APP_DB_URL)
AppSession = sessionmaker(bind=app_engine)