# scraping/fujikathailand.py

import requests
from requests.auth import HTTPBasicAuth
from utils.config import FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS


def fetch_fujika_posts(status="publish", limit=10):
    """
    ดึงโพสต์จากเว็บไซต์ fujikathailand.com ผ่าน REST API
    status: publish, private, draft
    """
    url = f"https://fujikathailand.com/wp-json/wp/v2/posts?status={status}&per_page={limit}"
    auth = HTTPBasicAuth(FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS)

    response = requests.get(url, auth=auth)

    if response.status_code == 200:
        posts = []
        for post in response.json():
            posts.append({
                "id": post["id"],
                "title": post["title"]["rendered"],
                "link": post["link"],
                "date": post["date"]
            })
        return posts
    else:
        print("Error:", response.status_code)
        return []
