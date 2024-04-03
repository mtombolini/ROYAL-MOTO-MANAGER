import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/fe52edd6684e3bed679ba68ca4850fe8/raw/68062ae30d50de377dc0b7b860594f920f3e6e8c/suppliers"

CONNECTIONS = "https://gist.githubusercontent.com/franco-anfossi/4bea704c796a6a2a36429b56b9ad3767/raw/034915a3eccc70cb4aa1b39560104a4dc6b6dd28/conections-suppliers"

response_suppliers = requests.get(SUPPLIERS)
data_suppliers = json.loads(response_suppliers.text)

response_connections = requests.get(CONNECTIONS)
data_connections = json.loads(response_connections.text)

df_suppliers = pd.DataFrame(data_suppliers)
df_connections = pd.DataFrame(data_connections)