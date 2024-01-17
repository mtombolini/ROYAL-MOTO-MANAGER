import time
import threading

from databases.session import AppSession

from app.config import config
from app.dataframe_main import DataFrameMain
from app.flags import stop_flag, stop, stop_signal_is_set, clear_stop_signal

from api.extractors.sales_extractor import SalesExtractor
from api.extractors.product_extractor import ProductExtractor
from api.extractors.returns_extractor import ReturnsExtractor
from api.extractors.document_extractor import DocumentExtractor
from api.extractors.shipping_extractor import ShippingExtractor
from api.extractors.reception_extractor import ReceptionExtractor
from api.extractors.price_list_extractor import PriceListExtractor
from api.extractors.consumption_extractor import ConsumptionExtractor

from services.analysis.analysis_main import Analyser

# TOKEN = "7a9dc44e2b4e17845a8199844e30a055f6754a9c"
TOKEN = config['development_postgres'].TOKEN

product_ext = ProductExtractor(token=TOKEN)
reception_ext = ReceptionExtractor(token=TOKEN)
consumption_ext = ConsumptionExtractor(token=TOKEN)
sales_ext = SalesExtractor(token=TOKEN)
returns_ext = ReturnsExtractor(token=TOKEN)
document_ext = DocumentExtractor(token=TOKEN)
price_list_ext = PriceListExtractor(token=TOKEN)
shipping_ext = ShippingExtractor(token=TOKEN)

def run_threads(dataframe_main, analyser , threads):
    for thread in threads:
        thread.start()

    while any(thread.is_alive() for thread in threads):
        if stop_signal_is_set():
            print("Señal de detención detectada. Esperando a que las threads terminen.")
            break
        time.sleep(0.1)

    session = AppSession()
    try:
        dataframe_main.create_data_base(session)
        analyser.main(session)
    finally:
        session.close()

def main():
    dataframe_main = DataFrameMain()
    analyser = Analyser()
    clear_stop_signal()
    try:
        threads = [
            threading.Thread(target=product_ext.run, args=(dataframe_main,)),
            threading.Thread(target=reception_ext.run, args=(dataframe_main,)),
            threading.Thread(target=consumption_ext.run, args=(dataframe_main,)),
            threading.Thread(target=sales_ext.run, args=(dataframe_main,)),
            threading.Thread(target=returns_ext.run, args=(dataframe_main,)),
            threading.Thread(target=document_ext.run, args=(dataframe_main,)),
            threading.Thread(target=price_list_ext.run, args=(dataframe_main,)),
            threading.Thread(target=shipping_ext.run, args=(dataframe_main,))
        ]

        while True:
            stop_flag.clear()
            print("Inicializando threads.")
            run_threads(dataframe_main, analyser, threads)

            if stop_signal_is_set():
                print("Proceso de detención en curso.")
                raise KeyboardInterrupt
            
            print("Todos los threads han terminado. Reiniciando ciclo.")
            time.sleep(10)
            break

    except KeyboardInterrupt:
        print("Interrupción detectada, enviando señal de detención a los threads...")
        stop()

    print("Limpieza y salida del programa.")

if __name__ == "__main__":
    main()