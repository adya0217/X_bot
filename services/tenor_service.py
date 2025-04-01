import requests
from utils.logging_utils import log_message
import os
import random

class TenorService:
    def __init__(self):
        self.api_key = os.getenv("TENOR_API_KEY")
        self.base_url = "https://tenor.googleapis.com/v2"

    def search_gif(self, keywords):
        try:
            query = " ".join(keywords)
            url = f"{self.base_url}/search"
            params = {
                "q": query,
                "key": self.api_key,
                "limit": 10,
                "media_filter": "gif"
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json()["results"]
                if results:
                    # Randomly select one GIF from results
                    gif = random.choice(results)
                    return gif["media_formats"]["gif"]["url"]
            return None
        except Exception as e:
            log_message(f"Error fetching Tenor GIF: {e}")
            return None 