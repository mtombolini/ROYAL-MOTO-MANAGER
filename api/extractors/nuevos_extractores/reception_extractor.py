import time
import json
import pandas as pd

from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class ConsumptionExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_receptions = None
        self.df_receptions_details = None

        self.receptions = []
        self.receptions_details = []

        self.reception_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"stocks/receptions.json?limit={self.limit}&offset={self.offset}&expand=[details, office]"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} recepciones obtenidas")

            self.write_logs()

        self.df_receptions = pd.DataFrame(self.receptions)
        self.df_receptions_details = pd.DataFrame(self.receptions_details)

    def main_extraction(self, response):
        for reception in response['items']:
            if stop_signal_is_set():
                return
            
            self.reception_id = reception['id']

            self.create_main_dataframe(reception)
            self.create_detail_dataframe(reception)

    def create_main_dataframe(self, reception):
        admission_date = reception['admissionDate']
        document = reception['document']
        document_number = reception['documentNumber']
        office = reception['office']['name']
        note = reception['note']

        self.receptions.append({
            'ID': int(self.reception_id),
            'Admission Date': self.convert_to_date(admission_date),
            'Document': document,
            'Document Number': document_number,
            'Office': office,
            'Note': note
        })

    def create_detail_dataframe(self, reception):
        details = reception['details']
        details_count = details['count']

        if details_count <= 25:
            self.less_than_25_details(details)
        else:
            self.more_than_25_details(details)

    def less_than_25_details(self, details):
        for detail in details['items']:
            detail_id = int(detail['id'])
            variant_id = int(detail['variant']['id'])
            quantity = int(detail['quantity'])
            cost = float(detail['cost'])
            
            self.receptions_details.append({
                'Detail ID': detail_id,
                'Reception ID': int(self.reception_id),
                'Variant ID': variant_id,
                'Quantity': quantity,
                'Net Cost': cost
            })

    def more_than_25_details(self, details):
        details_link = details['href'][24:]
        details_limit = 50
        details_offset = 0
        while True:
            endpoint = f"{details_link}?limit={details_limit}&offset={details_offset}"
            details = self.make_request(endpoint)
            if details is None or len(details['items']) == 0:
                break
            else:
                self.less_than_25_details(details)

            details_offset += details_limit

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "recepciones", "mensaje": f"{self.offset} recepciones obtenidas"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Recepciones...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "recepciones-listo", "mensaje": f"Recepciones ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_receptions = self.df_receptions
            dataframe_main.df_receptions_details = self.df_receptions_details

if __name__ == "__main__":
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    extractor = ConsumptionExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo recepciones...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_receptions, "reception_data.xlsx")
    extractor.save_to_excel(extractor.df_receptions_details, "reception_details_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")