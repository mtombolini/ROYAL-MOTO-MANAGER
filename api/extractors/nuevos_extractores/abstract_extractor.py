import os
import requests
import datetime
import pandas as pd

from abc import ABC, abstractmethod

class DataExtractor(ABC):
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }
        self.token = token
        self.base_url = "https://api.bsale.io/v1/"
        self.limit = 50
        self.offset = 0

    @abstractmethod
    def get_data(self):
        pass

    def make_request(self, endpoint, method="GET", data=None):
        url = self.base_url + endpoint
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # para hacer funcionar los get_first descomentar las lineas de abajo
            # print(f"Error: {e}.")
            # raise
            return None

    @staticmethod
    def convert_to_date(timestamp_unix):
        return datetime.datetime.utcfromtimestamp(timestamp_unix).strftime('%Y-%m-%d %H:%M:%S')

    def save_to_excel(self, df, file_name):
        mode = 'a' if os.path.exists(file_name) else 'w'
        with pd.ExcelWriter(file_name, engine='openpyxl', mode=mode) as writer:
            df.to_excel(writer, index=False)

    @abstractmethod
    def run(self, dataframe_main):
        pass

