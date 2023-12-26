import asyncio
from sqlalchemy.orm import Session
from databases.session import AppSession
from models.productos import Product, ProductStock

def save_products_to_db(df, session: Session):
    products = [
        Product(
            variant_id=row['variant_id'],
            sku=row['SKU'],
            tipo=row['Tipo'],
            descripcion=row['Descripcion']
        ) for _, row in df.iterrows()
    ]
    session.add_all(products)
    session.commit()

def save_stocks_to_db(df, session: Session):
    products = [
        ProductStock(
            variant_id=row['variant_id'],
            stock_lira=row['stock_lira'],
            stock_sobrexistencia=row['stock_sobrexistencia'],
        ) for _, row in df.iterrows()
    ]
    session.add_all(products)
    session.commit()

async def fetch_and_save_products(api):
    products_df = await api.obtener_productos()
    with AppSession() as session:
        save_products_to_db(products_df, session)
    print(f"Productos (descripcion) guardados en la base de datos.")

async def fetch_and_save_stocks(api):
    products_df = await api.obtener_stocks()
    with AppSession() as session:
        save_stocks_to_db(products_df, session)
    print(f"Productos (stock) guardados en la base de datos.")

