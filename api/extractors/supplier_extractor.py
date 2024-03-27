import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/fe52edd6684e3bed679ba68ca4850fe8/raw/f94c3fab7120783567c1cfe68837b9e67d9c8329/suppliers"

CONNECTIONS = "https://gist.githubusercontent.com/franco-anfossi/4bea704c796a6a2a36429b56b9ad3767/raw/109f23cb65b2a4add7582c8af374e0d9c95c29b9/conections-suppliers"

response_suppliers = requests.get(SUPPLIERS)
data_suppliers = json.loads(response_suppliers.text)

response_connections = requests.get(CONNECTIONS)
data_connections = json.loads(response_connections.text)

df_suppliers = pd.DataFrame(data_suppliers)
df_connections = pd.DataFrame(data_connections)