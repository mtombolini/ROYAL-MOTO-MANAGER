import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/fe52edd6684e3bed679ba68ca4850fe8/raw/8ff53edf6cf44c27ca9d1f8d0b352f1041fd6e00/suppliers"

CONNECTIONS = "https://gist.githubusercontent.com/franco-anfossi/4bea704c796a6a2a36429b56b9ad3767/raw/109f23cb65b2a4add7582c8af374e0d9c95c29b9/conections-suppliers"

response_suppliers = requests.get(SUPPLIERS)
data_suppliers = json.loads(response_suppliers.text)

response_connections = requests.get(CONNECTIONS)
data_connections = json.loads(response_connections.text)

df_suppliers = pd.DataFrame(data_suppliers)
df_connections = pd.DataFrame(data_connections)