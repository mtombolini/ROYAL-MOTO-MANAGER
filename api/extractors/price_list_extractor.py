import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class PriceListExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_price_list = None
        self.price_list = []

        self.price_id = None

        self.id_list = [6, 9, 11]
        self.name_list = [
            "Lista de Precios Base",
            "Lista de Precios Mercado Libre",
            "Lista de Precios Web"
        ]

        self.num = 0

    def get_data(self):
        while self.num != 3 and not stop_signal_is_set():
            endpoint = f"price_lists/{self.id_list[self.num]}/details.json?limit={self.limit}&offset={self.offset}"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                self.offset = 0
                self.num += 1
                
            else:
                self.main_extraction(response)

                self.offset += self.limit
                print(f"{self.offset} precios obtenidos")

                self.write_logs()

        self.df_price_list = pd.DataFrame(self.price_list)

    def main_extraction(self, response):
        for price_list in response['items']:
            if stop_signal_is_set():
                return
            
            self.price_id = price_list['id']

            self.create_main_dataframe(price_list)

    def create_main_dataframe(self, price_list):
        value = price_list['variantValueWithTaxes']
        variant_id = price_list['variant']['id']

        self.price_list.append({
            'List ID': int(self.id_list[self.num]),
            'Name': self.name_list[self.num],
            'Detail ID': int(self.price_id),
            'Value': float(value),
            'Variant ID': int(variant_id)
        })

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "listas_precio", "mensaje": f"{self.name_list[self.num]}: {self.offset} precios obtenidos"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Listas de Precios...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "lista_precios-listo", "mensaje": f"Lista de Precios ✅"})
                log_file.write(message + "\n")
                
            dataframe_main.df_price_list = self.df_price_list

if __name__ == "__main__":
    extractor = PriceListExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo listas de precios...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_price_list, "price_list_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")