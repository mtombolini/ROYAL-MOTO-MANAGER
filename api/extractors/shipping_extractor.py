import requests
import pandas as pd
import os
import time
import datetime
import json
from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

class ShippingExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_shippings = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.shippings = []

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

    def get_shippings(self):
        while not stop_signal_is_set():
            response = self.make_request(f"shippings.json?limit={self.limit}&offset={self.offset}&expand=[shipping_type, guide, document_type]")
            
            if response is None or len(response['items']) == 0:
                break
            else:

                if stop_signal_is_set():
                    return

                for shipping in response['items']:
                    shipping_id = shipping['id']
                    shipping_date = self.convert_to_date(shipping['shippingDate'])
                    shipping_number = shipping.get('guide', {}).get('number')
                    document_type = shipping.get('guide', {}).get('document_type', {}).get('name')
                    shipping_type = shipping['shipping_type']['name']

                    self.shippings.append({
                        'ID': int(shipping_id),
                        'Shipping Date': shipping_date,
                        'Shipping Number': shipping_number,
                        'Shipping Type': shipping_type,
                        'Document Type': document_type
                    })

            self.offset += self.limit
            print(f"{self.offset} despachos obtenidas")

            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "despachos", "mensaje": f"{self.offset} despachos obtenidos"})
                log_file.write(message + "\n")
            
        self.df_shippings = pd.DataFrame(self.shippings)

    def save_to_excel(self, file_name="despacho_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_shippings is not None:
                self.df_shippings.to_excel(writer, sheet_name='Despachos', index=False)

    def run(self, dataframe_main):
        print("Obteniendo despachos...")
        self.get_shippings()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "despachos-listo", "mensaje": f"Despachos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_shippings = self.df_shippings

        # print("Guardando recepciones en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ShippingExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo despachos...")
    extractor.get_shippings()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")