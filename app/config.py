#from parameters import PASSWORD_MYSQL, PASSWORD_POSTGRES
class Config:
    SECRET_KEY = '909932'
    BASE_URL = 'https://api.bsale.io/v1/'
    TOKEN_PATH = 'Api/token.txt'
    STOCKS_DATABASE_NAME = 'royal_manager_stocks' 

class DevelopmentConfigMySQL(Config):
    DEBUG = True
    HOST = 'localhost'
    USER = 'root'
    #PASSWORD = PASSWORD_MYSQL
    DB = 'royal_manager_database'
    API_DATA_RESET_MODE = True
    #DATA_BASE_URL = f"mysql+mysqldb://{USER}:{PASSWORD}@{HOST}/{DB}"

class DevelopmentConfigPostgres(Config):
    DEBUG = True
    HOST = 'localhost'
    USER = 'postgres'
    #PASSWORD = PASSWORD_POSTGRES
    DB = 'royal_manager_database'
    API_DATA_RESET_MODE = True
    #DATA_BASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}/{DB}"

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