import os
import pandas as pd
import time
import asyncio
import aiohttp
import json
import requests
# from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

class ProductExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_products_description = None
        self.df_products_stock = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.products = []
        self.stocks = []

# ------  FUNCIONES PARA HACER LLAMADOS Y OBTENER EL PRIMER PRODUCTO Y STOCK  ------

    def make_request(self, endpoint, method="GET", data=None):
        url = self.base_url + endpoint
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # para hacer funcionar los get_first descomentar las lineas de abajo
            # print(f"Error: {e}.")
            # raise
            return None

# ------  FUNCIONES PARA OBTENER LOS DATOS DE LA API  ------

    def get_consumption(self):
        while True:
            response = self.make_request(f"variants.json?limit={self.limit}&offset={self.offset}&expand=[product_type]")

            if response is None or len(response['items']) == 0:
                break
            else:
                for product in response['items']:
                    variant_id = product['id']
                    sku = product['code']
                    estado = product['state']
                    product_name = product['product']['name']
                    product_type_name = product['product']['product_type']['name']


                    self.products.append({
                        'Variant ID': int(variant_id),
                        'Product Type': product_type_name,
                        'Product Description': product_name,
                        'SKU': sku,
                        'State': estado
                    })

            self.offset += self.limit
            print(f"{self.offset} productos obtenidos")

            # with open("logs/api_status.log", "a") as log_file:
            #     message = json.dumps({"tipo": "consumos", "mensaje": f"{self.offset} consumos obtenidos"})
            #     log_file.write(message + "\n")
            
        self.df_products_description = pd.DataFrame(self.products)

    def get_consumptions(self):
        while True:
            response = self.make_request(f"stocks.json?limit={self.limit}&offset={self.offset}&expand=[office]")

            if response is None or len(response['items']) == 0:
                break
            else:
                for stock in response['items']:
                    variant_id = stock['variant']['id']
                    office = stock['office']['name']
                    quantity = stock['quantity']

                    self.products.append({
                        'Variant ID': int(variant_id),
                        'Office': office,
                        'Quantity': int(quantity)
                    })

            self.offset += self.limit
            print(f"{self.offset} productos obtenidos")

            # with open("logs/api_status.log", "a") as log_file:
            #     message = json.dumps({"tipo": "consumos", "mensaje": f"{self.offset} consumos obtenidos"})
            #     log_file.write(message + "\n")
            
        self.df_products_description = pd.DataFrame(self.products)
        pivot_df = self.df_products_description.pivot_table(index='Variant ID', columns='Office', values='Quantity', fill_value=0)

        pivot_df.columns = [f'Stock {col}' for col in pivot_df.columns]
        pivot_df.index.name = 'Variant ID'

        self.df_products_description = pivot_df


    def save_to_excel(self, file_name="products_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_products_description is not None:
                self.df_products_description.to_excel(writer, sheet_name='Productos', index=True)

    def run(self, dataframe_main):
        print("Obteniendo consumptions...")
        self.get_consumptions()

        if True:
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "consumos-listo", "mensaje": f"Consumos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_consumptions = self.df_consumptions
            dataframe_main.df_consumptions_details = self.df_consumptions_details

        # print("Guardando consumos en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ProductExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo PRODUCTOS...")
    extractor.get_consumptions()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")