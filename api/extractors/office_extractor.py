import time
import json
import pandas as pd

from app.config import TOKEN
from app.flags import stop_signal_is_set
from api.extractors.abstract_extractor import DataExtractor

from models.office import Office
from databases.session import AppSession

class OfficeExtractor(DataExtractor):
    def __init__(self, token):
        super().__init__(token)

        self.df_offices = None

        self.offices = []

        self.office_id = None

    def get_data(self):
        while not stop_signal_is_set():
            endpoint = f"offices.json?limit={self.limit}&offset={self.offset}"
            response = self.make_request(endpoint)

            if response is None or len(response['items']) == 0:
                break
            else:
                self.main_extraction(response)

            self.offset += self.limit
            print(f"{self.offset} sucursales obtenidas")

            self.write_logs()

        self.df_offices = pd.DataFrame(self.offices)

    def main_extraction(self, response):
        for office in response['items']:
            if stop_signal_is_set():
                return
            
            self.office_id = office['id']

            self.create_main_dataframe(office)

    def create_main_dataframe(self, office):
        name = office['name']
        address = office['address']
        municipality = office['municipality']
        city = office['city']
        country = office['country']
        active_state = office['state']
        latitude = office['latitude']
        longitude = office['longitude']

        self.offices.append({
            'ID': int(self.office_id),
            'Nombre': name,
            'Dirección': address,
            'Comuna': municipality,
            'Ciudad': city,
            'Pais': country,
            'Estado': active_state,
            'Latitud': latitude,
            'Longitud': longitude
        })

    def write_logs(self):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "sucursales", "mensaje": f"{self.offset} sucursales obtenidas"})
            log_file.write(message + "\n")

    def run(self, dataframe_main):
        print("Obteniendo Sucursales...")
        self.get_data()

        if not stop_signal_is_set():
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "sucursales-listo", "mensaje": f"Sucursales ✅"})
                log_file.write(message + "\n")

            dataframe_main.df_offices = self.df_offices

if __name__ == "__main__":
    extractor = OfficeExtractor(token=TOKEN)
    time_start = time.time()

    print("Obteniendo sucursales...")
    extractor.get_data()
    session = AppSession()
    for index, row in extractor.df_offices.iterrows():
        office = Office(
            id=int(row['ID']),
            name=row['Nombre'],
            address=row['Dirección'],
            municipality=row['Comuna'],
            city=row['Ciudad'],
            country=row['Pais'],
            active_state=row['Estado'],
            latitude=row['Latitud'],
            longitude=row['Longitud']
        )
        session.add(office)

    session.commit()
    session.close()

    # print("Guardando datos en Excel...")
    # extractor.save_to_excel(extractor.df_offices, "sucursales_data.xlsx")

    print("¡Proceso finalizado!")
    print(f"Tiempo total: {time.time() - time_start} segundos")