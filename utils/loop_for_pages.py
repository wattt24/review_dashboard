from utils.token_manager import auto_refresh_token
from api.facebook_graph_api import get_page_posts
import os
page_tokens = {}
for page_id in os.getenv("FACEBOOK_PAGE_IDS"):
    token = auto_refresh_token("facebook_page", page_id)
    if token:
        page_tokens[page_id] = token

# ใช้ page_tokens เรียก API ของแต่ละเพจ
for page_id, token in page_tokens.items():
    posts = get_page_posts(page_id, token)
    print(f"Posts for page {page_id}:", posts)
