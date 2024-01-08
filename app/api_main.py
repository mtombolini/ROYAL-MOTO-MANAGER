import threading
import time

from api.extractors.reception_extractor import ReceptionExtractor
from api.extractors.product_extractor import ProductExtractor
from api.extractors.consumption_extractor import ConsumptionExtractor
from api.extractors.sales_extractor import SalesExtractor
from api.extractors.returns_extractor import ReturnsExtractor
from api.extractors.document_extractor import DocumentExtractor
from app.dataframe_main import DataFrameMain

from databases.session import AppSession

TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"
    
time_start = time.time()
print("Inicializando")

dataframe_main = DataFrameMain()

product_ext = ProductExtractor(token=TOKEN)
reception_ext = ReceptionExtractor(token=TOKEN)
consumption_ext = ConsumptionExtractor(token=TOKEN)
sales_ext = SalesExtractor(token=TOKEN)
returns_ext = ReturnsExtractor(token=TOKEN)
document_ext = DocumentExtractor(token=TOKEN)

thread_product = threading.Thread(target=product_ext.run, args=(dataframe_main,))
thread_reception = threading.Thread(target=reception_ext.run, args=(dataframe_main,))
thread_consumption = threading.Thread(target=consumption_ext.run, args=(dataframe_main,))
thread_sales = threading.Thread(target=sales_ext.run, args=(dataframe_main,))
thread_returns = threading.Thread(target=returns_ext.run, args=(dataframe_main,))
thread_document = threading.Thread(target=document_ext.run, args=(dataframe_main,))

thread_reception.start()
thread_consumption.start()
thread_sales.start()
thread_returns.start()
thread_document.start()
thread_product.start()

thread_product.join()
thread_reception.join()
thread_consumption.join()
thread_sales.join()
thread_returns.join()
thread_document.join()

session = AppSession()
dataframe_main.create_data_base(session)
session.close()

print(f"Tiempo de ejecución: {time.time() - time_start} segundos")
print("¡Proceso finalizado!")