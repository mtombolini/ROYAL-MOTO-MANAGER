import requests
import pandas as pd
import os
import time
import datetime
import json

class DocumentExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_documents = None
        self.df_documents_detailes = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.documents = []
        self.documents_detailes = []

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
    
    def get_documents(self):
        while True:
            response = self.make_request(f"documents.json?limit={1}&offset={self.offset}&expand=[details, document_type, office]")
            
            if response is None or len(response['items']) == 0:
                break
            
            if False:
                return

            for document in response['items']:
                document_id = document['id']
                document_date = document['generationDate']
                document_number = document['number']
                document_total_amount = document['totalAmount']
                document_net_amount = document['netAmount']
                document_type = document['document_type']['name']
                document_office = document['office']['name']
            
                details = document['details']

                self.documents.append({
                    'Document ID': int(document_id),
                    'Document Date': self.convert_to_date(document_date),
                    'Document Number': document_number,
                    'Office': document_office,
                    'Total Amount': float(document_total_amount),
                    'Net Amount': float(document_net_amount),
                    'Document Type': document_type
                })

                if details['count'] <= self.limit:
                    for detail in details['items']:
                        detail_id = int(detail['id'])
                        detail_variant_id = int(detail['variant']['id'])
                        detail_quantity = int(detail['quantity'])
                        detail_net_unit_value = float(detail['netUnitValue'])
                        detail_net_total_value = float(detail['totalUnitValue'])

                        self.documents_detailes.append({
                            'Document ID': document_id,
                            'Detail ID': detail_id,
                            'Variant ID': detail_variant_id,
                            'Quantity': detail_quantity,
                            'Net Unit Value': detail_net_unit_value,
                            'Net Total Value': detail_net_total_value
                        })

                else:
                    details_limit = 50
                    details_offset = 0
                    while True:
                        details = self.make_request(f"{details['href'][24:]}?limit={details_limit}&offset={details_offset}")
                        if details is None or len(details['items']) == 0:
                            break

                        for detail in details['items']:
                            detail_id = int(detail['id'])
                            detail_variant_id = int(detail['variant']['id'])
                            detail_quantity = int(detail['quantity'])
                            detail_net_unit_value = float(detail['netUnitValue'])
                            detail_net_total_value = float(detail['totalUnitValue'])

                            self.documents_detailes.append({
                                'Document ID': document_id,
                                'Detail ID': detail_id,
                                'Variant ID': detail_variant_id,
                                'Quantity': detail_quantity,
                                'Net Unit Value': detail_net_unit_value,
                                'Net Total Value': detail_net_total_value
                            })

                        details_offset += details_limit

            self.offset += self.limit
            print(f"{self.offset} documentos obtenidos")

            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "documentos", "mensaje": f"{self.offset} documentos obtenidos"})
                log_file.write(message + "\n")

        self.df_documents = pd.DataFrame(self.documents).drop_duplicates(subset='Document ID', keep='first')
        self.df_documents_detailes = pd.DataFrame(self.documents_detailes).drop_duplicates(subset='Detail ID', keep='first')

    def save_to_excel(self, file_name="document_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_documents is not None:
                self.df_documents.to_excel(writer, sheet_name='Documents', index=False)

            if self.df_documents_detailes is not None:
                self.df_documents_detailes.to_excel(writer, sheet_name='Documents Details', index=False)

    def run(self, dataframe_main):
        print("Obteniendo documentos...")
        self.get_documents()
        
        if True:
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "documentos-listo", "mensaje": f"Documentos ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_documents = self.df_documents
            dataframe_main.df_documents_details = self.df_documents_detailes

        # print("Guardando documentos en Excel...")
        # self.save_to_excel()
    

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = DocumentExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo documentos...")
    extractor.get_documents()

    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    #extractor.save_to_excel()

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")