import requests
import pandas as pd
import os
import time
import datetime

class ConsumptionExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_consumptions_details = None
        self.df_consumptions = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.consumptions = []
        self.consumptions_details = []

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

    def get_consumptions(self):
        while True:
            response = self.make_request(f"stocks/consumptions.json?limit={self.limit}&offset={self.offset}&expand=[details]")
            if response is None or len(response['items']) == 0:
                break
            else:
                for consumption in response['items']:
                    consumption_id = consumption['id']
                    consumption_date = consumption['consumptionDate']
                    note = consumption['note']
                    details = consumption['details']
                    details_count = details['count']
                    details_link = details['href'][24:]

                    self.consumptions.append({
                        'ID': int(consumption_id),
                        'Consumption Date': self.convert_to_date(consumption_date),
                        'Note': note
                    })

                    if details_count <= self.limit:
                        for detail in details['items']:
                            detail_id = int(detail['id'])
                            variant_id = int(detail['variant']['id'])
                            quantity = int(detail['quantity'])
                            cost = float(detail['cost'])

                            self.consumptions_details.append({
                                'Detail ID': detail_id,
                                'Consumption ID': consumption_id,
                                'Variant ID': variant_id,
                                'Quantity': quantity,
                                'Net Cost': cost
                            })

                    else:
                        details_limit = 50
                        details_offset = 0
                        while True:
                            details = self.make_request(f"{details_link}?limit={details_limit}&offset={details_offset}")
                            if details is None or len(details['items']) == 0:
                                break
                            else:
                                for detail in details['items']:
                                    detail_id = int(detail['id'])
                                    variant_id = int(detail['variant']['id'])
                                    quantity = int(detail['quantity'])
                                    cost = float(detail['cost'])

                                    self.consumptions_details.append({
                                        'Detail ID': detail_id,
                                        'Consumption ID': consumption_id,
                                        'Variant ID': variant_id,
                                        'Quantity': quantity,
                                        'Net Cost': cost
                                    })

                            details_offset += details_limit

            self.offset += self.limit
            print(f"{self.offset} cosumos obtenidas")
            
        self.df_consumptions = pd.DataFrame(self.consumptions)
        self.df_consumptions_details = pd.DataFrame(self.consumptions_details)

    def save_to_excel(self, file_name="consumption_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_consumptions is not None:
                self.df_consumptions.to_excel(writer, sheet_name='Consumption', index=False)

            if self.df_consumptions_details is not None:
                self.df_consumptions_details.to_excel(writer, sheet_name='Consumption Details', index=False)

    def run(self, dataframe_main):
        print("Obteniendo consumptions...")
        self.get_consumptions()

        dataframe_main.df_consumptions = self.df_consumptions
        dataframe_main.df_consumptions_details = self.df_consumptions_details

        # print("Guardando consumos en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ConsumptionExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo consumptions...")
    extractor.get_consumptions()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")