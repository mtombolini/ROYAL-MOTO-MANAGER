import asyncio
from sqlalchemy.orm import Session
from loaders.api_product import fetch_and_save_products, fetch_and_save_stocks
from loaders.api_receptions import fetch_and_save_receptions
from api.extractors.bsale_products import BsaleAPIProductos
from api.extractors.bsale_receptions import BsaleAPIReceptions
from app.config import config

# def delete_all_from_product_db(session: Session):
#     session.query(ProductStock).delete()
#     session.query(ProductDescription).delete()
#     session.commit()

# def delete_all_from_document_db(session: Session):
#     session.query(Reception).delete()
#     session.commit()

if __name__ == "__main__":
    current_config = config['development']
    
    api_productos = BsaleAPIProductos("5ebe57568c598e5a9e2decd8f8ed2076a561e3a4")
    api_ingresos = BsaleAPIReceptions("5ebe57568c598e5a9e2decd8f8ed2076a561e3a4")

    # if current_config.API_DATA_RESET_MODE:
    #     with ProductSession() as session:
    #         delete_all_from_product_db(session)

    #     with DocumentSession() as session:
    #         delete_all_from_document_db(session)

    #     print("Reseteo de bases de datos completado")

    # Crear un único loop para manejar todas las tareas asincrónicas
    loop = asyncio.get_event_loop()

    # Ejecutar las tareas asincrónicas para productos y stocks
    loop.run_until_complete(fetch_and_save_products(api_productos))
    loop.run_until_complete(fetch_and_save_stocks(api_productos))

    # Ejecutar la tarea asincrónica para las recepciones
    loop.run_until_complete(fetch_and_save_receptions(api_ingresos))

    # Cerrar el loop después de usarlo
    loop.close()

    print("Llenado de base de datos completado")
