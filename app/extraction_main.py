import time

from app.api_main import ApiMain
from databases.session import AppSession
from services.analysis.analysis_main import Analyser

class ExtractionMain:
    def run_extraction(self):
        api_main = ApiMain()
        api_main.main()

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