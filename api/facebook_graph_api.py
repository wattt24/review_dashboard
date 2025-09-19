# api/facebook_graph_api.py
import requests
from utils.token_manager import auto_refresh_token

def get_page_info(page_id: str):
    """
    ดึงข้อมูลเพจจาก Facebook Graph API
    """
    ACCESS_TOKEN = auto_refresh_token("facebook", page_id)
    if not ACCESS_TOKEN:
        return {"error": f"⚠️ ไม่มี token สำหรับเพจ {page_id}"}

    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {
        "fields": "id,name,picture{url}",
        "access_token": ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()
    return res


def get_page_posts(page_id: str, limit: int = 5):
    """
    ดึงโพสต์ล่าสุดจากเพจ
    """
    ACCESS_TOKEN = auto_refresh_token("facebook", page_id)
    if not ACCESS_TOKEN:
        return {"error": f"⚠️ ไม่มี token สำหรับเพจ {page_id}"}

    url = f"https://graph.facebook.com/v19.0/{page_id}/posts"
    params = {
        "fields": "id,message,created_time,permalink_url",
        "limit": limit,
        "access_token": ACCESS_TOKEN
    }

    res = requests.get(url, params=params).json()
    return res


def get_page_insights(page_id: str, metric: str = "page_impressions,page_engaged_users"):
    """
    ดึงข้อมูล Insights (เช่น Reach, Engagement)
    """
    ACCESS_TOKEN = auto_refresh_token("facebook", page_id)
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
    result = auto_refresh_token(shop_id, endpoint, params)
    if "items" in result:
        return result["items"]
    return []