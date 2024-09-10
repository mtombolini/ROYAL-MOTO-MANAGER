from models.productos import Product
from models.product_activation import ProductActivation
from databases.session import AppSession


def init_product_activation():
    session = AppSession()

    try:
        # Recupera todos los SKUs únicos de la tabla de productos
        products_skus = session.query(Product.sku).all()
        
        # Por cada SKU, crea un nuevo ProductActivation con is_active en False
        for sku_tuple in products_skus:
            sku = sku_tuple[0]
            exists = session.query(ProductActivation.sku).filter_by(sku=sku).first() is not None
            if not exists:
                new_activation = ProductActivation(sku=sku, is_active=True)
                session.add(new_activation)
        
        # Confirma los cambios en la base de datos
        session.commit()
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        session.rollback()
    finally:
        session.close()