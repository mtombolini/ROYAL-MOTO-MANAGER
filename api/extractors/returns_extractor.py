import requests
import pandas as pd
import os
import time
import datetime
import json
from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

class ReturnsExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_returns = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.returns = []

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

    def get_returns(self):
        while not stop_signal_is_set():
            response = self.make_request(f"returns.json?&limit={self.limit}&offset={self.offset}")
            if response is None or len(response['items']) == 0:
                break
            
            for devoluciones in response['items']:

                if stop_signal_is_set():
                    return

                return_id = devoluciones['id']
                document_id = devoluciones['reference_document']['id']

                if 'credit_note' in devoluciones:
                    credit_note_id = devoluciones['credit_note']['id']
                else:
                    credit_note_id = None

                self.returns.append({
                    'Return ID': int(return_id),
                    'Document ID': int(document_id),
                    'Credit Note ID': credit_note_id
                })

            self.offset += self.limit
            print(f"{self.offset} devoluciones obtenidas")

            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "devoluciones", "mensaje": f"{self.offset} devoluciones obtenidos"})
                log_file.write(message + "\n")
        
        self.df_returns = pd.DataFrame(self.returns)

    def save_to_excel(self, file_name="returns_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_returns is not None:
                self.df_returns.to_excel(writer, sheet_name='Returns', index=False)

    def run(self, dataframe_main):
        print("Obteniendo devoluciones...")
        self.get_returns()
        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "devoluciones-listo", "mensaje": f"Devoluciones ✅"})
                log_file.write(message + "\n")
            dataframe_main.df_returns = self.df_returns

        # print("Guardando devoluciones en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = ReturnsExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo devoluciones...")
    extractor.get_returns()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")