from models.productos import Product
from services.stock_manager.simple.test import predict

class Analyser:
    def __init__(self):
        self.ids = []
        self.products = self.get_all()
        self.kardexs = {}

    def get_all(self):
        return Product.get_all_products()
    
    def get_ids(self):
        for product in self.products:
            self.ids.append(product['variant_id'])

    def get_kardexs(self):
        for id in self.ids:
            product_data = Product.filter_product(id)
            self.kardexs[id] = product_data['kardex']

    def analyse(self):
        pass
