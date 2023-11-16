from .cart import BuyCart, BuyCartDetail
from databases.session import CartSession

class ModelCart:

    @classmethod
    def get_all_carts(cls):
        session = CartSession()
        try:
            carts = session.query(BuyCart).all()
            return carts
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    @classmethod
    def delete_cart_by_id(cls, cart_id):
        session = CartSession()
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
    def get_cart_detail_by_id(cls, cart_id):
        session = CartSession()
        try:
            cart_detail = session.query(BuyCartDetail).filter(BuyCartDetail.cart_id == cart_id).all()
            cart_general = session.query(BuyCart).filter(BuyCart.cart_id == cart_id).first()
            return cart_general, cart_detail
        except Exception as ex:
            raise Exception(ex)
        finally:
            session.close()

    
