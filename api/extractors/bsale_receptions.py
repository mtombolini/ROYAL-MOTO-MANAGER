import json
import aiohttp
import certifi
import ssl
import asyncio
import os
import pandas as pd
import datetime

class BsaleAPIReceptions:
    BASE_URL = 'https://api.bsale.io/v1/'

    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }
        self.df_recepciones = None
        self.df_details = None
        self.max = 50

    def convertir_unix_a_fecha(self, timestamp_unix):
        return datetime.datetime.utcfromtimestamp(timestamp_unix).strftime('%Y-%m-%d %H:%M:%S')

    async def _request(self, session, endpoint, method="GET", data=None):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        retries = 10
        delay = 30

        for _ in range(retries):
            async with session.request(method, self.BASE_URL + endpoint, headers=self.headers, json=data, ssl=ssl_context) as response:
                if response.status == 429:
                    print(f"Error 429: Demasiadas solicitudes. Esperando {delay} segundos antes de reintentar...")
                    await asyncio.sleep(delay)
                    continue
                elif response.status != 200:
                    raise Exception(f"Error {response.status}: {await response.text()}")
                return await response.json()

    async def obtener_detalles_recepcion(self, session, reception_id, offset=0):
        endpoint = f"stocks/receptions/{reception_id}/details.json"
        all_details = []
        limit = 50

        while True:
            respuesta = await self._request(session, f"{endpoint}?limit={limit}&offset={offset}")
            if 'items' in respuesta and respuesta['items']:
                for item in respuesta['items']:
                    item['reception_id'] = reception_id
                    all_details.append(item)
                if len(respuesta['items']) < limit:
                    break
                offset += limit
            else:
                break

        return all_details

    async def obtener_recepciones(self):
        endpoint = "stocks/receptions.json"
        all_receptions = []
        all_details = []
        offset = 0
        limit = 50

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as session:
            tasks = []  # Declara tasks aquí
            while offset <= self.max:
                respuesta = await self._request(session, f"{endpoint}?limit={limit}&offset={offset}")
                print(f'Obteniendo Recepciones: Offset {offset}')
                
                if 'items' in respuesta and respuesta['items']:
                    for item in respuesta['items']:
                        reception = {
                            'id': item['id'],
                            'admissionDate': item['admissionDate'],
                            'document': item['document'],
                            'note': item['note']
                        }
                        all_receptions.append(reception)
                        tasks.append(self.obtener_detalles_recepcion(session, item['id']))

                    offset += limit
                else:
                    break

            # Convertir fechas después de recopilar todas las recepciones.
            for reception in all_receptions:
                reception['admissionDate'] = self.convertir_unix_a_fecha(reception['admissionDate'])

            results = await asyncio.gather(*tasks)
            for details in results:
                for detail in details:
                    all_details.append(detail)

        self.df_recepciones = pd.DataFrame(all_receptions)
        self.df_recepciones = self.df_recepciones.filter(items=["id", "admissionDate", "document", "note"])
        self.df_details = pd.DataFrame(all_details)
        self.df_details['variant_id'] = self.df_details['variant'].apply(lambda x: x['id'])
        self.df_details = self.df_details.filter(items=["id", "reception_id", "quantity", "cost", "variant_id"])

        return self.df_recepciones, self.df_details

    def guardar_en_excel(self, df=None, filename='recepciones.xlsx'):
        if df is not None:
            current_directory = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.abspath(os.path.join(current_directory, filename))
            df.to_excel(filepath, index=False)
            print(f"Datos exportados a {filename}")

if __name__ == "__main__":
    api = BsaleAPIReceptions("e84dd5e43387cd3777d801c0ac4eb12816ecd30d")
    loop = asyncio.get_event_loop()
    recepciones_df, detalles_df = loop.run_until_complete(api.obtener_recepciones())
    
    api.guardar_en_excel(recepciones_df, 'recepciones.xlsx')
    api.guardar_en_excel(detalles_df, 'detalles_recepciones.xlsx')

    loop.close()
