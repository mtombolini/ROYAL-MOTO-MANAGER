import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

class DocumentExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_documents = None
        self.df_documents_details = None

        self.documents = []
        self.documents_details = []

        self.document_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"documents.json?limit={self.limit}&offset={self.offset}&expand=[details, document_type, office]"
            response = self.make_request(endpoint)
            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} documentos obtenidos")

            self.write_logs()

        self.df_documents = pd.DataFrame(self.documents).drop_duplicates(subset='Document ID', keep='first')
        self.df_documents_details = pd.DataFrame(self.documents_details).drop_duplicates(subset='Detail ID', keep='first')

    def main_extraction(self, response):
        for document in response['items']:
            if stop_signal_is_set():
                return
            
            self.document_id = document['id']

            self.create_main_dataframe(document)
            self.create_detail_dataframe(document)

    def create_main_dataframe(self, document):
        document_date = document['generationDate']
        document_number = document['number']
        document_total_amount = document['totalAmount']
        document_net_amount = document['netAmount']
        document_type = document['document_type']['name']
        document_office = document['office']['name']

        self.documents.append({
            'Document ID': int(self.document_id),
            'Document Date': self.convert_to_date(document_date),
            'Document Number': document_number,
            'Office': document_office,
            'Total Amount': float(document_total_amount),
            'Net Amount': float(document_net_amount),
            'Document Type': document_type
        })

    def create_detail_dataframe(self, document):
        details = document['details']
        details_count = details['count']

        if details_count <= 25:
            self.less_than_25_details(details)
        else:
            self.more_than_25_details(details)

    def less_than_25_details(self, details):
        for detail in details['items']:
            detail_id = int(detail['id'])
            detail_variant_id = int(detail['variant']['id'])
            detail_quantity = int(detail['quantity'])
            detail_net_unit_value = float(detail['netUnitValue'])
            detail_net_total_value = float(detail['totalUnitValue'])

            self.documents_details.append({
                'Document ID': self.document_id,
                'Detail ID': detail_id,
                'Variant ID': detail_variant_id,
                'Quantity': detail_quantity,
                'Net Unit Value': detail_net_unit_value,
                'Net Total Value': detail_net_total_value
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
            message = json.dumps({"tipo": "documentos", "mensaje": f"{self.offset} documentos obtenidos"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Documentos...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "documentos-listo", "mensaje": f"Documentos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_documents = self.df_documents
            dataframe_main.df_documents_details = self.df_documents_details

if __name__ == "__main__":
    extractor = DocumentExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo documentos...")
    extractor.get_data()

    print("Guardando datos en Excel...")
    extractor.save_to_excel(extractor.df_documents, "document_data.xlsx")
    extractor.save_to_excel(extractor.df_documents_details, "document_details_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")