import requests
from utils.logging_utils import log_message
import os
import random

class UnsplashService:
    def __init__(self):
        self.api_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.base_url = "https://api.unsplash.com"

    def search_image(self, keywords):
        try:
            query = " ".join(keywords)
            url = f"{self.base_url}/search/photos"
            headers = {
                "Authorization": f"Client-ID {self.api_key}"
            }
            params = {
                "query": query,
                "per_page": 10,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                results = response.json()["results"]
                if results:
                    # Randomly select one image from results
                    image = random.choice(results)
                    return image["urls"]["regular"]
            return None
        except Exception as e:
            log_message(f"Error fetching Unsplash image: {e}")
            return None 