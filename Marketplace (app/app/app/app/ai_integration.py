import requests

class AIIntegration:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_art(self, prompt):
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={'text': prompt},
            headers={'api-key': self.api_key}
        )
        return response.json()
