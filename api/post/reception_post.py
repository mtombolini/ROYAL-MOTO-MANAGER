import requests
from app.config import TOKEN

class ReceptionPost:
    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'access_token': token
        }
        self.token = token
        self.base_url = "https://api.bsale.io/v1/"
        
    def make_request(self, endpoint, method="POST", data=None):
        url = self.base_url + endpoint
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()  # Lanza una excepción para respuestas fallidas
            return response.json()
        except requests.RequestException as e:
            # Descomenta estas líneas si deseas manejar los errores de manera específica
            # print(f"Error: {e}.")
            # raise
            return None
        
    def send_data(self, post_data):
        endpoint = "stocks/receptions.json"
        response = self.make_request(endpoint, data=post_data)
        
        return response

if __name__ == "__main__":
    post_data = {}
    reception_post = ReceptionPost(TOKEN)
    reception_post.send_data(post_data)