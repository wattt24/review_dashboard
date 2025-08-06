# scraping/facebook_scraper.py
import requests
from utils.config import FB_PAGE_ID, FB_ACCESS_TOKEN

def fetch_fb_posts(limit=10):
    url = f"https://graph.facebook.com/v17.0/{FB_PAGE_ID}/posts?access_token={FB_ACCESS_TOKEN}&limit={limit}"
    r = requests.get(url)
    return r.json().get("data", [])