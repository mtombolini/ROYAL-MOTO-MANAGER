import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class ShippingExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_shippings = None

        self.shippings = []

        self.shipping_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"shippings.json?limit={self.limit}&offset={self.offset}&expand=[shipping_type, guide, document_type]"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} despachos obtenidos")

            self.write_logs()

        self.df_shippings = pd.DataFrame(self.shippings)

    def main_extraction(self, response):
        for shipping in response['items']:
            if stop_signal_is_set():
                return
            
            self.shipping_id = shipping['id']

            self.create_main_dataframe(shipping)

    def create_main_dataframe(self, shipping):
        shipping_date = self.convert_to_date(shipping['shippingDate'])
        state = shipping['state']
        shipping_number = shipping.get('guide', {}).get('number')
        document_type = shipping.get('guide', {}).get('document_type', {}).get('name')
        shipping_type = shipping['shipping_type']['name']

        self.shippings.append({
            'ID': int(self.shipping_id),
            'Shipping Date': shipping_date,
            'Shipping Number': shipping_number,
            'Shipping Type': shipping_type,
            'Document Type': document_type,
            'State': state
        })

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "despachos", "mensaje": f"{self.offset} despachos obtenidos"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Despachos...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "despachos-listo", "mensaje": f"Despachos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_shippings = self.df_shippings

if __name__ == "__main__":
    extractor = ShippingExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo devoluciones...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_shippings, "shipping_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")