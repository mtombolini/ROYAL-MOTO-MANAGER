from models.productos import Product

class LastNetCostExtractor:
    def __init__(self):
        self.ids = Product.get_all_products_ids()

    def last_net_cost_creation(self):
        for variant_id in self.ids:
            Product.get_product_reception(variant_id, 0, False)

    def main_extraction(self):
        self.last_net_cost_creation()
    
if __name__ == "__main__":
    extractor = LastNetCostExtractor()
    extractor.main_extraction()
