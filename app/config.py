import os
from dotenv import load_dotenv

load_dotenv('.env')

class Config:
    API_DATA_RESET_MODE = True
    TOKEN = os.environ.get('SECRET_TOKEN')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    CONFIG_TYPE = os.environ.get('CONFIG_TYPE', 'development')
    DEBUG = (os.environ.get('DEBUG', 'False').lower() == 'true')
    DEFAULT_DATABASE_URL = os.environ.get('DEFAULT_DATABASE_URL')

CONFIG = Config()
TOKEN = CONFIG.TOKEN