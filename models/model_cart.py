from models.cart import BuyCart, BuyCartDetail
from databases.session import AppSession
from sqlalchemy import text

class ModelCart:
    @classmethod
    def get_all_carts(cls):
        session = AppSession()
        try:
            carts = session.query(BuyCart).all()
            return carts
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def get_cart_by_id(cls, cart_id):
        session = AppSession()
        try:
            cart = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def get_receptioned_carts(cls):
        session = AppSession()
        try:
            carts = session.query(BuyCart).filter(BuyCart.estado == 'Recepcionada').all()
            return carts
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def delete_cart_by_id(cls, cart_id):
        session = AppSession()
        try:
            cart_to_delete = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            if cart_to_delete:
                session.delete(cart_to_delete)
                session.commit()
                return True
            else:
                return False
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def delete_cart_detail_by_id(cls, cart_detail_id):
        session = AppSession()
        try:
            cart_detail_to_delete = session.query(BuyCartDetail).filter(BuyCartDetail.id == cart_detail_id).first()
            if cart_detail_to_delete:
                session.delete(cart_detail_to_delete)
                session.commit()
                return True
            else:
                return False
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def get_cart_detail_by_id(cls, cart_id):
        session = AppSession()
        try:
            cart_detail = session.query(BuyCartDetail).filter(BuyCartDetail.cart_id == cart_id).all()
            cart_general = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            return cart_general, cart_detail
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def create_cart(cls, cart_data):
        session = AppSession()
        try:
            result = session.execute(text("SELECT MAX(cart_id) FROM carros_compras"))
            max_id = result.scalar()
            cart = BuyCart(
                cart_id = max_id + 1,
                descripcion=cart_data['descripcion'],
                fecha_creacion=cart_data['fecha_creacion'],
                fecha_recepcion=cart_data['fecha_creacion'],
                proveedor=cart_data['proveedor'],
                rut=cart_data['rut'],
                razon_social=cart_data['razon_social'],
                monto_neto=cart_data['monto_neto'],
                cantidad_productos=cart_data['cantidad_productos'],
                estado=cart_data['estado'],
                revision=cart_data['revision'],
                rendimiento=cart_data['rendimiento']
            )
            session.add(cart)
            session.commit()
            session.refresh(cart)

            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def create_cart_detail(cls, cart_detail_data):
        session = AppSession()
        try:
            result = session.execute(text("SELECT MAX(id) FROM carros_compras_detalles"))
            max_id = result.scalar()
            cart_detail = BuyCartDetail(
                id=max_id + 1,
                cart_id=cart_detail_data['cart_id'],
                variant_id=cart_detail_data['variant_id'],
                descripcion_producto=cart_detail_data['descripcion_producto'],
                sku_producto=cart_detail_data['sku_producto'],
                costo_neto=cart_detail_data['costo_neto'],
                cantidad=cart_detail_data['cantidad']
            )
            session.add(cart_detail)
            session.commit()
            session.refresh(cart_detail)
            return cart_detail
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def update_cart(cls, cart_id, costo, cantidad):
        session = AppSession()
        try:
            cart = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            cart.monto_neto += costo
            cart.cantidad_productos += cantidad
            session.commit()
            session.refresh(cart)
            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def check_to_update_all_cart(cls, cart_id):
        session = AppSession()
        try:
            cart = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            cantidad = 0
            costo = 0
            for detail in cart.details:
                cantidad += detail.cantidad
                costo += detail.cantidad * detail.costo_neto

            cart.monto_neto = costo
            cart.cantidad_productos = cantidad

            session.commit()
            session.refresh(cart)
            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def update_cart_detail(cls, cart_detail_id, cantidad, costo):
        session = AppSession()
        try:
            cart_detail = session.query(BuyCartDetail).filter(BuyCartDetail.id == cart_detail_id).first()
            cart_detail.cantidad = cantidad
            cart_detail.costo_neto = costo

            session.commit()
            session.refresh(cart_detail)
            return cart_detail
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def update_cart_status(cls, cart_id, estado):
        session = AppSession()
        try:
            cart = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            cart.estado = estado

            session.commit()
            session.refresh(cart)
            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def update_cart_datatime(cls, cart_id, fecha_recepcion):
        session = AppSession()
        try:
            cart = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            cart.fecha_recepcion = fecha_recepcion

            session.commit()
            session.refresh(cart)
            return cart
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()