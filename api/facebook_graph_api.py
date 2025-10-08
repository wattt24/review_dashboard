# api/facebook_graph_api.py
import requests
from utils.token_manager import get_latest_token



def get_page_info(page_id: str):
    """ดึงข้อมูลพื้นฐานของเพจ (ชื่อ + โลโก้)"""
    token_data = get_latest_token("facebook", page_id)
    if not token_data or not token_data.get("access_token"):
        return {"error": f"ไม่พบ token สำหรับเพจ {page_id}"}

    PAGE_TOKEN = token_data["access_token"]
    url_page = f"https://graph.facebook.com/v23.0/{page_id}"
    params = {"fields": "id,name,picture{url}", "access_token": PAGE_TOKEN}

    res = requests.get(url_page, params=params).json()
    if "error" in res:
        return {"error": res["error"]}
    return res


def get_page_posts(page_id: str, limit: int = 3):
    """ดึงโพสต์ล่าสุด"""
    token_data = get_latest_token("facebook", page_id)
    if not token_data or not token_data.get("access_token"):
        return []

    PAGE_TOKEN = token_data["access_token"]
    url = f"https://graph.facebook.com/v23.0/{page_id}/posts"
    params = {
        "access_token": PAGE_TOKEN,
        "limit": limit,
        "fields": "id,message,created_time,permalink_url"
    }
    res = requests.get(url, params=params).json()
    return res.get("data", [])


def get_page_reviews(page_id: str, limit: int = 5):
    """ดึงรีวิวล่าสุด"""
    token_data = get_latest_token("facebook", page_id)
    if not token_data or not token_data.get("access_token"):
        return []

    PAGE_TOKEN = token_data["access_token"]
    url = f"https://graph.facebook.com/v23.0/{page_id}/ratings"
    params = {
        "access_token": PAGE_TOKEN,
        "limit": limit,
        "fields": "id,recommendation_type,review_text,created_time,reviewer"
    }
    res = requests.get(url, params=params).json()
    return res.get("data", [])


def get_post_comments(post_id, page_token, limit=10):
    """ดึงคอมเมนต์จากโพสต์"""
    url = f"https://graph.facebook.com/v23.0/{post_id}/comments"
    params = {
        "access_token": page_token,
        "limit": limit,
        "fields": "from{name,id},message,created_time"
    }
    res = requests.get(url, params=params).json()
    return res.get("data", [])


def get_page_insights(page_id: str, metric: str = "page_impressions,page_engaged_users"):
    """
    ดึงข้อมูล Insights (เช่น Reach, Engagement)
    """
    ACCESS_TOKEN = get_latest_token("facebook", page_id)
    if not ACCESS_TOKEN:
        return {"error": f"⚠️ ไม่มี token สำหรับเพจ {page_id}"}

    url = f"https://graph.facebook.com/v19.0/{page_id}/insights"
    params = {
        "metric": metric,
        "period": "day",
        "access_token": ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()
    return res
def get_top_selling_items(shop_id: int, limit: int = 5):
    """
    ดึงสินค้าขายดีจาก Shopee
    """
    endpoint = "/api/v2/item/get_shop_items"
    params = {
        "shop_id": shop_id,
        "order_by": "sales",
        "page_size": limit,
    }
    result = get_latest_token(shop_id, endpoint, params)
    if "items" in result:
        return result["items"]
    return []