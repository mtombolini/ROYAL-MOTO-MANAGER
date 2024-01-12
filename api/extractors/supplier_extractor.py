import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/06a273959c67287a879980dba725b248/raw/9d7d64208e770a725b36ce3cdf709dc934d75632/gistfile1.txt"

response = requests.get(SUPPLIERS)

data = json.loads(response.text)

df_suppliers = pd.DataFrame(data)