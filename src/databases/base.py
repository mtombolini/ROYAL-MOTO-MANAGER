from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Define la cadena de conexión a tu base de datos
DATABASE_URL = "mysql+mysqldb://[USERNAME]:[PASSWORD]@[HOST]/[DB_NAME]"

# Crea el motor de la base de datos
engine = create_engine(DATABASE_URL)

# Define la base declarativa para tus modelos
UserBase = declarative_base()
ProductBase = declarative_base()
DocumentBase = declarative_base()
CartsBase = declarative_base()

# Crea una fábrica de sesiones para interactuar con la base de datos
SessionLocal = sessionmaker(bind=engine)
