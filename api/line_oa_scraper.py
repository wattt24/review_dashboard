# scraping/line_oa_scraper.py
import requests
from utils.config import LINE_CHANNEL_ACCESS_TOKEN

def get_line_summary():
    url = "https://api.line.me/v2/bot/message/delivery/reply"
    headers = {"Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers)
    return r.json()