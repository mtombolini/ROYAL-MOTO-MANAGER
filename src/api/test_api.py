import json
import aiohttp
import certifi
import ssl
import asyncio
import os
import pandas as pd

class BsaleAPIProductos:
    BASE_URL = 'https://api.bsale.io/v1/'

    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }
        self.df_productos_descripción = None
        self.df_productos_stock = None
        self.max = 1000000

    async def _request(self, session, endpoint, method="GET", data=None):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        retries = 10
        delay = 50

        for _ in range(retries):
            async with session.request(method, self.BASE_URL + endpoint, headers=self.headers, json=data, ssl=ssl_context) as response:
                if response.status == 429:
                    print(f"Error 429: Demasiadas solicitudes. Esperando {delay} segundos antes de reintentar...")
                    await asyncio.sleep(delay)
                    continue
                elif response.status != 200:
                    raise Exception(f"Error {response.status}: {await response.text()}")
                return await response.json()

        raise Exception("Error 429: Demasiadas solicitudes después de varios reintentos.")

    async def obtener_productos(self):
        endpoint = "products.json"
        all_products = []
        offset = 0
        limit = 50
        processed_variants = set()  # Validaciones adicionales

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as session:

            while offset < self.max:
                respuesta = await self._request(session, f"{endpoint}?expand=[variants,product_type]&fields=name,id&limit={limit}&offset={offset}")
                
                if 'items' in respuesta and respuesta['items']:
                    for product in respuesta['items']:
                        product_name = product['name']
                        product_type_name = product['product_type']['name']
                        
                        for variant in product['variants']['items']:
                            variant_id = variant['id']
                            if variant_id in processed_variants:
                                print(f"Variant ya procesado: {variant_id}")
                                continue
                            processed_variants.add(variant_id)
                            
                            all_products.append({
                                'variant_id': variant_id,
                                'Tipo': product_type_name,
                                'Descripcion': product_name,
                                'SKU': variant_id,
                            })

                    if len(respuesta['items']) < limit:
                        break

                    offset += limit
                    print(f'Obtener Productos N°: {offset}')
                else:
                    break

        self.df_productos_descripción = pd.DataFrame(all_products).drop_duplicates(subset='variant_id')  # Eliminar duplicados
        return self.df_productos_descripción

    async def obtener_stocks(self):
        endpoint = "stocks/3203.json"
        stock_data = {}
        offset = 0
        limit = 30

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as session:

            while offset < self.max:
                respuesta = await self._request(session, f"{endpoint}")
                print(respuesta)

                if 'items' in respuesta and respuesta['items']:
                    for stock_item in respuesta['items']:
                        variant_id = stock_item['variant']['id']

                        if variant_id == 3203:
                            print(respuesta)

                        if variant_id not in stock_data:
                            stock_data[variant_id] = {
                                'variant_id': variant_id,
                                'stock_lira': 0,
                                'stock_sobrexistencia': 0
                            }

                        if stock_item['office']['id'] == "1":
                            stock_data[variant_id]['stock_lira'] += stock_item['quantity']
                        elif stock_item['office']['id'] == "2":
                            stock_data[variant_id]['stock_sobrexistencia'] += stock_item['quantity']

                    offset += limit
                    print(f'Obtener Stocks N°: {offset}')
                else:
                    break

            self.df_productos_stock = pd.DataFrame(list(stock_data.values()))
            return self.df_productos_stock

    def guardar_en_excel(self, df, nombre):
        if df is not None:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.abspath(os.path.join(nombre))
            df.to_excel(filepath, index=False)
            print("Proceso exportado")

if __name__ == "__main__":
    api = BsaleAPIProductos("7a9dc44e2b4e17845a8199844e30a055f6754a9c")
    loop = asyncio.get_event_loop()
    #productos = loop.run_until_complete(api.obtener_productos())
    stock = loop.run_until_complete(api.obtener_stocks())
    #api.guardar_en_excel(productos, "productos.xlsx")
    api.guardar_en_excel(stock, "stocks.xlsx")
    loop.close()
