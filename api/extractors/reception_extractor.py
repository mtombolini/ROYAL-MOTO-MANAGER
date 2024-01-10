import requests
import pandas as pd
import os
import time
import datetime
import json
from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

class ReceptionExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_receptions_details = None
        self.df_receptions = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.receptions = []
        self.receptions_details = []

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

    def get_receptions(self):
        while not stop_signal_is_set():
            response = self.make_request(f"stocks/receptions.json?limit={self.limit}&offset={self.offset}&expand=[details]")
            if response is None or len(response['items']) == 0:
                break
            else:
                if stop_signal_is_set():
                    return

                for reception in response['items']:
                    reception_id = reception['id']
                    admission_date = reception['admissionDate']
                    document = reception['document']
                    note = reception['note']

                    details = reception['details']
                    details_count = details['count']
                    details_link = details['href'][24:]

                    self.receptions.append({
                        'ID': int(reception_id),
                        'Admission Date': self.convert_to_date(admission_date),
                        'Document': document,
                        'Note': note
                    })

                    if details_count <= self.limit:
                        for detail in details['items']:
                            detail_id = int(detail['id'])
                            variant_id = int(detail['variant']['id'])
                            quantity = int(detail['quantity'])
                            cost = float(detail['cost'])
                            
                            self.receptions_details.append({
                                'Detail ID': detail_id,
                                'Reception ID': int(reception_id),
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
                                    self.receptions_details.append({
                                        'Detail ID': detail_id,
                                        'Reception ID': int(reception_id),
                                        'Variant ID': variant_id,
                                        'Quantity': quantity,
                                        'Net Cost': cost
                                    })

                            details_offset += details_limit

            self.offset += self.limit
            print(f"{self.offset} recepciones obtenidas")

            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "recepciones", "mensaje": f"{self.offset} recepciones obtenidos"})
                log_file.write(message + "\n")
            
        self.df_receptions = pd.DataFrame(self.receptions)
        self.df_receptions_details = pd.DataFrame(self.receptions_details)

    def save_to_excel(self, file_name="reception_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_receptions is not None:
                self.df_receptions.to_excel(writer, sheet_name='Receptions', index=False)

            if self.df_receptions_details is not None:
                self.df_receptions_details.to_excel(writer, sheet_name='Reception Details', index=False)

    def run(self, dataframe_main):
        print("Obteniendo recepciones...")
        self.get_receptions()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "recepciones-listo", "mensaje": f"Recepciones ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_receptions = self.df_receptions
            dataframe_main.df_receptions_details = self.df_receptions_details

        # print("Guardando recepciones en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ReceptionExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo recepciones...")
    extractor.get_receptions()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")