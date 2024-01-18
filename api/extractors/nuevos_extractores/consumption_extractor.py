import time
import json
import pandas as pd

from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class ConsumptionExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_consumptions = None
        self.df_consumptions_details = None

        self.consumptions = []
        self.consumptions_details = []

        self.consumption_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"stocks/consumptions.json?limit={self.limit}&offset={self.offset}&expand=[details, office]"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} cosumos obtenidos")

            self.write_logs()

        self.df_consumptions = pd.DataFrame(self.consumptions)
        self.df_consumptions_details = pd.DataFrame(self.consumptions_details)

    def main_extraction(self, response):
        for consumption in response['items']:
            if stop_signal_is_set():
                return
            
            self.consumption_id = consumption['id']

            self.create_main_dataframe(consumption)
            self.create_detail_dataframe(consumption)

    def create_main_dataframe(self, consumption):
        consumption_date = consumption['consumptionDate']
        office = consumption['office']['name']
        note = consumption['note']

        self.consumptions.append({
            'ID': int(self.consumption_id),
            'Consumption Date': self.convert_to_date(consumption_date),
            'Office': office,
            'Note': note
        })

    def create_detail_dataframe(self, consumption):
        details = consumption['details']
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

            self.consumptions_details.append({
                'Detail ID': detail_id,
                'Consumption ID': self.consumption_id,
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
            message = json.dumps({"tipo": "consumos", "mensaje": f"{self.offset} consumos obtenidos"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Consumos...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "consumos-listo", "mensaje": f"Consumos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_consumptions = self.df_consumptions
            dataframe_main.df_consumptions_details = self.df_consumptions_details

if __name__ == "__main__":
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    extractor = ConsumptionExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo consumos...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_consumptions, "consumption_data.xlsx")
    extractor.save_to_excel(extractor.df_consumptions_details, "consumption_details_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")