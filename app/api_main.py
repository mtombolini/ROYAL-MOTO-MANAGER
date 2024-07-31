import time

from databases.session import AppSession

from app.config import TOKEN
from app.dataframe_main import DataFrameMain

from api.extractors.sales_extractor import SalesExtractor
from api.extractors.office_extractor import OfficeExtractor
from api.extractors.product_extractor import ProductExtractor
from api.extractors.returns_extractor import ReturnsExtractor
from api.extractors.document_extractor import DocumentExtractor
from api.extractors.shipping_extractor import ShippingExtractor
from api.extractors.reception_extractor import ReceptionExtractor
from api.extractors.price_list_extractor import PriceListExtractor
from api.extractors.consumption_extractor import ConsumptionExtractor

sales_ext = SalesExtractor(token=TOKEN)
office_ext = OfficeExtractor(token=TOKEN)
product_ext = ProductExtractor(token=TOKEN)
returns_ext = ReturnsExtractor(token=TOKEN)
document_ext = DocumentExtractor(token=TOKEN)
shipping_ext = ShippingExtractor(token=TOKEN)
reception_ext = ReceptionExtractor(token=TOKEN)
price_list_ext = PriceListExtractor(token=TOKEN)
consumption_ext = ConsumptionExtractor(token=TOKEN)


class ApiMain:
    def main(self):
        while True:
            dataframe_main = DataFrameMain()
            try:
                document_ext.run(dataframe_main)
                sales_ext.run(dataframe_main)
                product_ext.run(dataframe_main)
                reception_ext.run(dataframe_main)
                consumption_ext.run(dataframe_main)
                returns_ext.run(dataframe_main)
                price_list_ext.run(dataframe_main)
                shipping_ext.run(dataframe_main)
                office_ext.run(dataframe_main)

                print("Todos los threads han terminado. Reiniciando ciclo.")
                session = AppSession()
                try:
                    dataframe_main.create_data_base(session)
                finally:
                    session.close()
                    time.sleep(10)
                    break
            except Exception as e:
                print(f"Error en la ejecución: {e}")
                break

        print("Limpieza y salida del programa.")


if __name__ == "__main__":
    inicial = time.time()
    api_main = ApiMain()
    api_main.main()
    final = time.time()
    print(f"Tiempo total: {final - inicial} segundos.")
