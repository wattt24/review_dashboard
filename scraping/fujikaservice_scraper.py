
# scraping/fujikaservice_scraper.py
import requests
from utils.config import FUJIKA_SERVICE_API_KEY

def fetch_service_feedback():
    url = "https://fujikaservice.com/api/v1/feedback"
    headers = {"Authorization": f"Bearer {FUJIKA_SERVICE_API_KEY}"}
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []