import requests
import pandas as pd
import os
import time
import datetime
import json
# from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

class PriceListExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_price_list = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.price_list = []

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
    def convert_to_date(self, timestamp_unix):
        return datetime.datetime.utcfromtimestamp(timestamp_unix).strftime('%Y-%m-%d %H:%M:%S')

    def get_price_list(self):
        LISTA = [6, 9, 11]
        NOMBRE = ["Lista de Precios Base","Lista de Precios Mercado Libre","Lista de Precios Web"]
        I = 0
        while I != 3 and True: #not stop_signal_is_set():
            response = self.make_request(f"price_lists/{LISTA[I]}/details.json?limit={self.limit}&offset={self.offset}")
            
            if response is None or len(response['items']) == 0:
                self.offset = 0
                I += 1
            else:
                for price_list in response['items']:
                    # if stop_signal_is_set():
                    #     return

                    price_list_id = price_list['id']
                    value = price_list['variantValueWithTaxes']
                    variant_id = price_list['variant']['id']

                    self.price_list.append({
                        'ID': int(LISTA[I]),
                        'Name': NOMBRE[I],
                        'Detail ID': int(price_list_id),
                        'Value': float(value),
                        'Variant ID': int(variant_id)
                    })

                self.offset += self.limit
            print(f"{self.offset} precios obtenidas")

            # with open("logs/api_status.log", "a") as log_file:
            #     message = json.dumps({"tipo": "listas_de_precio", "mensaje": f"{self.offset} precios obtenidas"})
            #     log_file.write(message + "\n")
            
        self.df_price_list = pd.DataFrame(self.price_list)

    def save_to_excel(self, file_name="price_list_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_price_list is not None:
                self.df_price_list.to_excel(writer, sheet_name='Price List', index=False)

    def run(self, dataframe_main):
        print("Obteniendo price list...")
        self.get_price_list()

        if True: #not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "lista_precios-listo", "mensaje": f"Lista de Precios ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_price_list = self.df_price_list

        # print("Guardando consumos en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = PriceListExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo consumptions...")
    extractor.get_price_list()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")