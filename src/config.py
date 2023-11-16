from parameters import PASSWORD
class Config:
    SECRET_KEY = '909932'
    BASE_URL = 'https://api.bsale.io/v1/'
    TOKEN_PATH = 'Api/token.txt'
    STOCKS_DATABASE_NAME = 'royal_manager_stocks' 


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = PASSWORD
    MYSQL_DB = 'royal_manager_database'
    # MYSQL_DB_USERS_CONNECTION = 'royal_manager_user'
    # MYSQL_DB_PRODUCTS_CONNECTION = "royal_manager_products"
    # MYSQL_DB_DOCUMENTS_CONNECTION = "royal_manager_documents"
    # MYSQL_DB_CARTS_CONNECTION = "royal_manager_carts"
    API_DATA_RESET_MODE = True


config = {
    'development': DevelopmentConfig
}

