import time
import json
import pandas as pd

from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class ReturnsExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_returns = None

        self.returns = []

        self.return_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"returns.json?&limit={self.limit}&offset={self.offset}"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} devoluciones obtenidas")

            self.write_logs()

        self.df_returns = pd.DataFrame(self.returns)

    def main_extraction(self, response):
        for devolucion in response['items']:
            if stop_signal_is_set():
                return
            
            self.return_id = devolucion['id']

            self.create_main_dataframe(devolucion)

    def create_main_dataframe(self, devolucion):
        document_id = devolucion['reference_document']['id']

        if 'credit_note' in devolucion:
            credit_note_id = devolucion['credit_note']['id']
        else:
            credit_note_id = None

        self.returns.append({
            'Return ID': int(self.return_id),
            'Document ID': int(document_id),
            'Credit Note ID': credit_note_id
        })

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "devoluciones", "mensaje": f"{self.offset} devoluciones obtenidas"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Devoluciones...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "devoluciones-listo", "mensaje": f"Devoluciones ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_returns = self.df_returns

if __name__ == "__main__":
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    extractor = ReturnsExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo devoluciones...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_returns, "return_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")