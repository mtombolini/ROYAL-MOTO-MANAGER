import pandas as pd

# from databases.session import AppSession
from models.productos import Product
from models.day_recommendation import DayRecommendation
from services.stock_manager.simple.test import predict_no_plot

class Analyser:
    def __init__(self):
        self.ids = []
        self.products = self.get_all()
        self.kardexs = {}
        self.analysed = {}
        self.bad_ids = []

    def get_all(self):
        return Product.get_all_products()
    
    def get_ids(self):
        print('Obteniendo ids...')
        for product in self.products:
            self.ids.append(product['variant_id'])

    def get_kardexs(self):
        print('Obteniendo kardexs...')
        for id in self.ids:
            product_data = Product.filter_product(id, False)
            services = {'SERVICIO DE TALLER', 'SERVICIOS', 'SERVICIOS DE TALLER'}
            if not product_data['df_kardex'].empty and product_data['type'] not in services:
                self.kardexs[id] = product_data['df_kardex']
            else:
                self.bad_ids.append(id)

    def analyse(self):
        print('Analizando...')
        good_ids = [id for id in self.ids if id not in self.bad_ids]
        for id in good_ids:
            print(id)
            recommendation, date = predict_no_plot(self.kardexs[id])
            self.analysed[id] = {
                'recommendation': recommendation,
                'date': date
            }

    def create_model(self, session):
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