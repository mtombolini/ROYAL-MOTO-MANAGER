import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/06a273959c67287a879980dba725b248/raw/8db78e5910705c8307575f08fd40d9bafbbf9526/gistfile1.txt"

CONNECTIONS = "https://gist.githubusercontent.com/franco-anfossi/4d39e60b87b7161f0994212f2bd35a1a/raw/6724b052b71827862051515a227e1d234d0a97cd/gistfile1.txt"

response_suppliers = requests.get(SUPPLIERS)
data_suppliers = json.loads(response_suppliers.text)

response_connections = requests.get(CONNECTIONS)
data_connections = json.loads(response_connections.text)

df_suppliers = pd.DataFrame(data_suppliers)
df_connections = pd.DataFrame(data_connections)