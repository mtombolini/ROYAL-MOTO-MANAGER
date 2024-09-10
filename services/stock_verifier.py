from models.productos import Product, ProductStock
from models.supplier import Supplier

class StockVerifier:
    def __init__(self):
        self.ids = Product.get_all_products_ids()
        self.bad_skus = []
        self.sin_kardex = []

    def verify(self):
        for id in self.ids:
            product_data, _ = Product.filter_product(id, False)

            if len(product_data['kardex']) == 0:
                self.sin_kardex.append(product_data['sku'])
            elif product_data['stock']['stock_lira'] + product_data['stock']['stock_sobrexistencia'] != product_data['kardex'][-1]['stock_actual']:
                self.bad_skus.append(product_data['sku'])

if __name__ == '__main__':
    verifier = StockVerifier()
    verifier.verify()
    print(verifier.bad_skus)
    print(len(verifier.bad_skus))