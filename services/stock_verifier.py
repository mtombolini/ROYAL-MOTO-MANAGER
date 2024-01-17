from models.productos import Product, ProductStock
from models.supplier import Supplier

class StockVerifier:
    def __init__(self):
        self.ids = []
        self.products = self.get_all()
        self.bad_skus = []
        self.sin_kardex = []

    def get_all(self):
        return Product.get_all_products()
    
    def get_ids(self):
        for product in self.products:
            self.ids.append(product['variant_id'])
    
    def verify(self):
        for id in self.ids:
            product_data = Product.filter_product(id, True)

            if len(product_data['kardex']) == 0:
                self.sin_kardex.append(product_data['sku'])
            elif product_data['stock']['stock_lira'] + product_data['stock']['stock_sobrexistencia'] != product_data['kardex'][-1]['stock_actual']:
                self.bad_skus.append(product_data['sku'])

if __name__ == '__main__':
    verifier = StockVerifier()
    verifier.get_ids()
    verifier.verify()
    print(verifier.bad_skus)