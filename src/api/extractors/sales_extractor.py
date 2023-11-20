import requests
import pandas as pd
import os
import time
import datetime

class SalesExtractor:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }

        self.token = token
        self.df_sales = None
        self.df_relations = None
        self.base_url = "https://api.bsale.io/v1/"

        self.limit = 50
        self.offset = 0

        self.sales = []
        self.relations = []

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
    
    def get_sales(self):
        while True:
            response = self.make_request(f"payments.json?limit={self.limit}&offset={self.offset}&expand=[payment_type]")
            if response is None or len(response['items']) == 0:
                break

            for sale in response['items']:
                sale_id = sale['id']
                sale_date = sale['createdAt']
                sale_payment_type = sale['payment_type']['name']

                if 'document' in sale:
                    sale_document_id = [sale['document']['id']]
                elif 'documents' in sale:
                    sale_document_id = [especific_document['id'] for especific_document in sale['documents']]
                else:
                    sale_document_id = None

                self.sales.append({
                    'Sales ID': int(sale_id),
                    'Sale Date': self.convert_to_date(sale_date),
                    'Payment Type': sale_payment_type,
                    'Document ID': sale_document_id
                })

            self.offset += self.limit
            print(f"{self.offset} ventas obtenidas")
        
        self.df_sales = pd.DataFrame(self.sales)

    def correction(self):
        # Iteramos sobre cada fila del dataframe original
        for index, row in self.df_sales.iterrows():
            sales_id = row['Sales ID']
            # Verificamos si Document ID no es None y es una lista
            document_ids = row['Document ID']
            if document_ids is not None:
                for doc_id in document_ids:
                    # Añadimos la relación al listado
                    self.relations.append({'Sales ID': sales_id, 'Document ID': doc_id})
            else:
                # Si Document ID es None, se maneja según el caso de uso
                # Por ejemplo, podríamos querer añadir una fila con Document ID como None
                self.relations.append({'Sales ID': sales_id, 'Document ID': None})

        # Creamos el nuevo dataframe con las relaciones
        self.df_relations = pd.DataFrame(self.relations)

        # Insertamos la columna 'ID Support' como un índice autoincremental que inicia en 1
        self.df_relations.insert(0, 'ID Support', range(1, 1 + len(self.df_relations)))

        # Eliminamos la columna 'Document ID' del dataframe original
        self.df_sales.drop('Document ID', axis=1, inplace=True)

        # Podemos mostrar los primeros elementos de los dataframes como verificación
        print("DataFrame de Relaciones:")
        self.df_relations.head()

        print("\nDataFrame de Ventas Actualizado:")
        self.df_sales.head()

    def save_to_excel(self, file_name="sales_data.xlsx"):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            if self.df_sales is not None:
                self.df_sales.to_excel(writer, sheet_name='Sales', index=False)

            if self.df_relations is not None:
                self.df_relations.to_excel(writer, sheet_name='Sale-Document Relations', index=False)

    def run(self, dataframe_main):
        print("Obteniendo ventas...")
        self.get_sales()

        self.correction()

        dataframe_main.df_sales = self.df_sales
        dataframe_main.df_sales_documents = self.df_relations

        # print("Guardando ventas en Excel...")
        # self.save_to_excel()

if __name__ == "__main__":
    # Define tu token de autenticación aquí
    TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"

    # Crea una instancia de ProductExtractor
    extractor = SalesExtractor(token=TOKEN)
    time_start = time.time()

    # Obtener los variantes
    print("Obteniendo ventas...")
    extractor.get_sales()

    extractor.correction()
    
    # Guarda los datos en un archivo Excel
    print("Guardando datos en Excel...")
    extractor.save_to_excel()

    

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")