from requests.auth import HTTPBasicAuth
import requests
from utils.config import FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS

def fetch_comments_for_post(post_id, auth):# ใช้สําหรับดึงโพสและคอมเมนต์
    comments = []
    page = 1
    while True:
        url_comments = f"https://www.fujikathailand.com/wp-json/wp/v2/comments?post={post_id}&per_page=100&page={page}"
        response_comments = requests.get(url_comments, auth=auth)
        if response_comments.status_code == 404:
            # ไม่มีคอมเมนต์
            break
        response_comments.raise_for_status()
        data = response_comments.json()
        if not data:
            break
        comments.extend(data)
        # ถ้าจำนวนผลลัพธ์น้อยกว่าที่ขอแสดงว่าหน้านั้นสุดท้าย
        if len(data) < 100:
            break
        page += 1
    return comments

def fetch_posts_with_comments():
    url_posts = "https://www.fujikathailand.com/wp-json/wp/v2/posts"
    auth = HTTPBasicAuth(FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS)

    response_posts = requests.get(url_posts, auth=auth, timeout=10)
    response_posts.raise_for_status()
    posts = response_posts.json()

    posts_with_comments = []

    for post in posts:
        post_id = post["id"]
        comments = fetch_comments_for_post(post_id, auth)
        post["comments"] = comments
        posts_with_comments.append(post)

    return posts_with_comments
