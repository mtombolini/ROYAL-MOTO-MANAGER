import requests
from app.config import TOKEN

class ProductSearch:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }
        self.token = token
        self.base_url = "https://api.bsale.io/v1/"

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
        
    def get_data(self, code):
        endpoint = f"variants.json?code={code}&expand=[product, costs]"
        response = self.make_request(endpoint)

        if response is None or len(response['items']) == 0:
            return None
        else:
            data = {
                'count': response['count'],
                'variant id': response['items'][0]['id'],
                'sku': response['items'][0]['code'],
                'description': response['items'][0]['product']['name']
            }

            return data

if __name__ == "__main__":
    product_search = ProductSearch(TOKEN)
    product_search.get_data('1500')