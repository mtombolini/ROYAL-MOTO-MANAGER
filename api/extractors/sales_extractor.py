import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class SalesExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_sales = None
        self.df_relations = None

        self.sales = []
        self.relations = []

        self.sale_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"payments.json?limit={self.limit}&offset={self.offset}&expand=[payment_type]"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} ventas obtenidas")

            self.write_logs()

        self.df_sales = pd.DataFrame(self.sales)

    def main_extraction(self, response):
        for sale in response['items']:
            if stop_signal_is_set():
                return
            
            self.sale_id = sale['id']

            self.create_main_dataframe(sale)

    def create_main_dataframe(self, sale):
        sale_date = sale['createdAt']
        sale_payment_type = sale['payment_type']['name']

        if 'document' in sale:
            sale_document_id = [sale['document']['id']]
        elif 'documents' in sale:
            sale_document_id = [especific_document['id'] for especific_document in sale['documents']]
        else:
            sale_document_id = None

        self.sales.append({
            'Sales ID': int(self.sale_id),
            'Sale Date': self.convert_to_date(sale_date),
            'Payment Type': sale_payment_type,
            'Document ID': sale_document_id
        })

    def correction(self):
        for index, row in self.df_sales.iterrows():
            sales_id = row['Sales ID']
            document_ids = row['Document ID']
            if document_ids is not None:
                for doc_id in document_ids:
                    self.relations.append({'Sales ID': sales_id, 'Document ID': doc_id})
            else:
                self.relations.append({'Sales ID': sales_id, 'Document ID': None})

        self.df_relations = pd.DataFrame(self.relations)
        self.df_relations.insert(0, 'ID Support', range(1, 1 + len(self.df_relations)))
        self.df_sales.drop('Document ID', axis=1, inplace=True)

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "ventas", "mensaje": f"{self.offset} ventas obtenidas"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Ventas...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "ventas-listo", "mensaje": f"Ventas ✅"})
                log_file.write(message + "\n")

            self.correction()
            dataframe_main.df_sales = self.df_sales
            dataframe_main.df_sales_documents = self.df_relations

if __name__ == "__main__":
    extractor = SalesExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo ventas...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_sales, "sale_data.xlsx")
    extractor.save_to_excel(extractor.df_relations, "sale_document_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")