from parameters import PASSWORD_MYSQL, PASSWORD_POSTGRES, USER_MYSQL, USER_POSTGRES
class Config:
    SECRET_KEY = '909932'
    BASE_URL = 'https://api.bsale.io/v1/'
    TOKEN_PATH = 'Api/token.txt'
    STOCKS_DATABASE_NAME = 'royal_manager_stocks'
    TOKEN = '7a9dc44e2b4e17845a8199844e30a055f6754a9c'

class DevelopmentConfigMySQL(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5432
    USER = USER_MYSQL
    PASSWORD = PASSWORD_MYSQL
    DB = 'royal_manager_database'
    API_DATA_RESET_MODE = True
    DATA_BASE_URL = f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

class DevelopmentConfigPostgres(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5432
    USER = USER_POSTGRES
    PASSWORD = PASSWORD_POSTGRES
    DB = 'royal_manager_database'
    API_DATA_RESET_MODE = True
    DATA_BASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    DEFAULT_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/postgres"

class ProductionConfig(Config):
    DEBUG = False
    HOST = 'dpg-cm3tp1mn7f5s73brdhhg-a'
    USER = 'royal_motor_admin'
    PASSWORD = 'ePqyvJvmJRe1hOiwLiW9qCqI2VPVp4rl'
    DB = 'royal_motor_database'
    API_DATA_RESET_MODE = True
    DATA_BASE_URL = 'postgresql://royal_motor_admin:ePqyvJvmJRe1hOiwLiW9qCqI2VPVp4rl@dpg-cm3tp1mn7f5s73brdhhg-a.oregon-postgres.render.com/royal_motor_database'

config = {
    'development_mysql': DevelopmentConfigMySQL,
    'development_postgres': DevelopmentConfigPostgres,
    'production' : ProductionConfig
}

CONFIG = config['development_postgres']
TOKEN = CONFIG.TOKEN