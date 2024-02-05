import time

from app.api_main import ApiMain
from databases.session import AppSession
from services.analysis.analysis_main import Analyser
from api.extractors.last_net_cost_extractor import LastNetCostExtractor

class ExtractionMain:
    def run_extraction(self):
        api_main = ApiMain()
        api_main.main()

        last_net_cost_extractor = LastNetCostExtractor()
        last_net_cost_extractor.main_extraction()

        session = AppSession()
        analyser = Analyser()
        analyser.main(session)
        session.close()

if __name__ == '__main__':
    initial = time.time()
    extraction_main = ExtractionMain()
    extraction_main.run_extraction()
    final = time.time()
    print(f"Tiempo total: {final - initial} segundos")