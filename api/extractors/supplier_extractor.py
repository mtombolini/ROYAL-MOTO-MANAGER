import requests
import json
import pandas as pd

SUPPLIERS = "https://gist.githubusercontent.com/franco-anfossi/06a273959c67287a879980dba725b248/raw/d04ad1c9bc6178315342d1677a4e3232933e7953/gistfile1.txt"

response = requests.get(SUPPLIERS)

data = json.loads(response.text)

df_suppliers = pd.DataFrame(data)