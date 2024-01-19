import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class ProductExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_products = None
        self.df_stocks = None

        self.products = []
        self.stocks = []

        self.product_id = None
        self.stock_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"variants.json?limit={self.limit}&offset={self.offset}&expand=[product_type]"
            response = self.make_request(endpoint)

            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_product_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} productos obtenidos")

            self.write_product_logs()
            
        self.df_products = pd.DataFrame(self.products)
        self.df_products = self.df_products[self.df_products['State'] != 1]

        print("Obteniendo Stocks...")
        self.get_stocks()

    def main_product_extraction(self, response):
        for product in response['items']:
            if stop_signal_is_set():
                return
            
            self.product_id = product['id']
            
            self.create_main_product_dataframe(product)

    def create_main_product_dataframe(self, product):
        sku = product['code']
        estado = product['state']
        product_name = product['product']['name']
        product_type_name = product['product']['product_type']['name']

        self.products.append({
            'Variant ID': int(self.product_id),
            'Product Type': product_type_name,
            'Product Description': product_name,
            'SKU': sku,
            'State': estado
        })

    def write_product_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "productos", "mensaje": f"{self.offset} productos obtenidos"})
            log_file.write(message + "\n")

    def get_stocks(self):
        self.offset = 0
        while not stop_signal_is_set():
            endpoint = f"stocks.json?limit={self.limit}&offset={self.offset}&expand=[office]"
            response = self.make_request(endpoint)

            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_stock_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} stocks obtenidos")

            self.write_stock_logs()
            
        self.df_stocks = pd.DataFrame(self.stocks)
        
        self.order_stocks_dataframe()
        self.filter_products_by_stock()


    def main_stock_extraction(self, response):
        for stock in response['items']:
            if stop_signal_is_set():
                return
            
            self.stock_id = stock['variant']['id']
            
            self.create_main_stock_dataframe(stock)

    def create_main_stock_dataframe(self, stock):
        office = stock['office']['name']
        quantity = stock['quantity']

        self.stocks.append({
            'Variant ID': int(self.stock_id),
            'Office': office,
            'Quantity': int(quantity)
        })

    def write_stock_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "stocks", "mensaje": f"{self.offset} stocks obtenidos"})
            log_file.write(message + "\n")

    def order_stocks_dataframe(self):
        pivot_df = self.df_stocks.pivot_table(index='Variant ID', columns='Office', values='Quantity', fill_value=0)

        pivot_df.columns = [f'Stock {col.title()}' for col in pivot_df.columns]
        pivot_df.index.name = 'Variant ID'

        self.df_stocks = pivot_df.reset_index()

    def filter_products_by_stock(self):
        new_rows = []
        existing_variant_ids = set(self.df_stocks['Variant ID'])
        services = {'SERVICIO DE TALLER', 'SERVICIOS', 'SERVICIOS DE TALLER'}

        for index, row in self.df_products.iterrows():
            variant_id = row['Variant ID']
            if variant_id not in existing_variant_ids and row['Product Type'] in services:
                new_rows.append({
                    'Variant ID': variant_id,
                    'Stock Lira 823': 0,
                    'Stock Sobrexistencia': 0
                })

        if new_rows:
            self.df_stocks = pd.concat([self.df_stocks, pd.DataFrame(new_rows)], ignore_index=True)

        variant_ids = self.df_stocks['Variant ID'].values
        self.df_products = self.df_products[self.df_products['Variant ID'].isin(variant_ids)]
        self.df_stocks = self.df_stocks.sort_values(by='Variant ID')

    def run(self, dataframe_main):
        print("Obteniendo Productos...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "productos-listo", "mensaje": f"Productos ✅"})
                log_file.write(message + "\n")

            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "stocks-listo", "mensaje": f"Stocks ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_products = self.df_products
            dataframe_main.df_stocks = self.df_stocks

if __name__ == "__main__":
    extractor = ProductExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo Productos...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")
    