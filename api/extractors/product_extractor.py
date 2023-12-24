import os
import pandas as pd
import time
import asyncio
import aiohttp


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

    async def make_request(self, session, endpoint, method="GET", data=None):
        url = self.base_url + endpoint
        try:
            async with session.request(method, url, headers=self.headers, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            # Manejo de errores; ajusta según sea necesario
            print(f"Error: {e}.")
            return None

    async def get_variants(self):
        count = 0
        max_variant_id = 10000
        initial_variant_id = 3177

        async with aiohttp.ClientSession() as session:
            while initial_variant_id <= max_variant_id:
                product_response = await self.make_request(session, f"variants/{initial_variant_id}.json?expand=[product,product_type]")

                if product_response is not None:
                    variant_id = product_response['id']
                    sku = product_response['code']
                    product_name = product_response['product']['name']
                    product_type_name = product_response['product']['product_type']['name']

                    self.products.append({
                        'Variant ID': int(variant_id),
                        'Product Type': product_type_name,
                        'Product Description': product_name,
                        'SKU': sku
                    })

                    count += 1

                    if count % 50 == 0:
                        print(f"{count} variantes obtenidos")

                initial_variant_id += 1

        index = 0
        while len(self.products) != index:
            if self.products[index]['Product Description'] == '':
                self.products.pop(index)
            else:
                index += 1

        print("All products saved")
        self.df_products_description = pd.DataFrame(self.products).drop_duplicates(subset='Variant ID', keep='first')

        count = 0
        async with aiohttp.ClientSession() as session:
            for variant_id in self.df_products_description['Variant ID']:
                stock_response = await self.make_request(session, f"stocks.json?variantid={variant_id}")
                stock_items = stock_response['items']
                
                for stock_item in stock_items:
                    office_id = stock_item['office']['id']
                    quantity = stock_item['quantity']
                    if office_id == "1":
                        stock_lira = quantity
                    elif office_id == "2":
                        stock_sobrexistencia = quantity

                self.stocks.append({
                    'Variant ID': int(variant_id),
                    'Stock Lira': int(stock_lira),
                    'Stock Sobrexistencia': int(stock_sobrexistencia)
                })

                count += 1

                if count % 50 == 0:
                    print(f"{count} stocks obtenidos")

        print("All stocks saved")
        self.df_products_stock = pd.DataFrame(self.stocks).drop_duplicates(subset='Variant ID', keep='first')
    
    def save_to_excel(self, file_name="products_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_products_description is not None:
                self.df_products_description.to_excel(writer, sheet_name='Product Descriptions', index=False)

            if self.df_products_stock is not None:
                self.df_products_stock.to_excel(writer, sheet_name='Product Stocks', index=False)

    def run(self, dataframe_main):
        print("Obteniendo productos...")
        asyncio.run(self.get_variants())

        dataframe_main.df_products = self.df_products_description
        dataframe_main.df_stocks = self.df_products_stock

        # Guarda los datos en un archivo Excel
        # print("Guardando variantes en Excel...")
        # self.save_to_excel()


if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ProductExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo variantes...")
    asyncio.run(extractor.get_variants())

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")
