# scraping/cps_oem_scraper.py

import requests

def fetch_posts():
    url = "https://cpsmanu.com/wp-json/wp/v2/posts"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
