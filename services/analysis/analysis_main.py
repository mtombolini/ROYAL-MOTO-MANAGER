import pandas as pd
import json

# from databases.session import AppSession
from models.productos import Product
from models.day_recommendation import DayRecommendation
from services.stock_manager.simple.test import predict_no_plot

class Analyser:
    def __init__(self):
        self.ids = self.get_ids()
        self.kardexs = {}
        self.analysed = {}
        self.bad_ids = []

    def get_ids(self):
        return Product.get_all_products_ids()

    def get_kardexs(self):
        print('Obteniendo kardexs...')
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "analisis", "mensaje": f"Obteniendo kardexs..."})
            log_file.write(message + "\n")

        for id in self.ids:
            product_data, _ = Product.filter_product(id, False)
            services = {'SERVICIO DE TALLER', 'SERVICIOS', 'SERVICIOS DE TALLER'}
            if product_data['type'] not in services:
                df_kardex = product_data['df_kardex']
                df_kardex['fecha'] = pd.to_datetime(df_kardex['fecha']).dt.date
                unique_dates = df_kardex['fecha'].nunique()

                if unique_dates > 1:
                    self.kardexs[id] = df_kardex
                else:
                    self.bad_ids.append(id)
            else:
                self.bad_ids.append(id)

    def analyse(self):
        print('Analizando...')
        count = 0
        good_ids = [id for id in self.ids if id not in self.bad_ids]
        for id in good_ids:
            print(id)
            recommendation, date = predict_no_plot(self.kardexs[id])
            self.analysed[id] = {
                'recommendation': recommendation,
                'date': date
            }
            count += 1
            with open("logs/api_status.log", "a") as log_file:
                message = json.dumps({"tipo": "analisis", "mensaje": f"Analizando... {count}/{len(good_ids)}"})
                log_file.write(message + "\n")

    def create_model(self, session):
        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "analisis", "mensaje": f"Guardando recomendaciones..."})
            log_file.write(message + "\n")

        df_day_recommendation = pd.DataFrame.from_dict(self.analysed, orient='index').reset_index()
        df_day_recommendation.rename(columns={'index': 'variant_id'}, inplace=True)

        for index, row in df_day_recommendation.iterrows():
            day_recommendation = DayRecommendation(
                variant_id = row['variant_id'],
                recommendation = row['recommendation'],
                date = row['date']
            )
            session.add(day_recommendation)

        session.commit()

        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "analisis", "mensaje": f"Recomendaciones guardadas"})
            log_file.write(message + "\n")

        with open("logs/api_status.log", "a") as log_file:
            message = json.dumps({"tipo": "analisis-listo", "mensaje": f"Analisis ✅"})
            log_file.write(message + "\n")

    def main(self, session):
        self.get_ids()
        self.get_kardexs()
        self.analyse()
        self.create_model(session)

if __name__ == '__main__':
    analyser = Analyser()
    analyser.get_ids()
    analyser.get_kardexs()
    analyser.analyse()
    # session = AppSession()
    # analyser.create_model(session)
    # session.close()