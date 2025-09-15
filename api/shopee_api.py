# api/shopee_api.py
import requests
import time  # สำหรับ timestamp (ใน call_shopee_api เรียกใช้)
from services.shopee_auth import call_shopee_api_auto,shopee_generate_sign,get_token # ฟังก์ชัน generic caller
BASE_URL = "https://partner.shopeemobile.com"
from utils.token_manager import save_token
from utils.config import SHOPEE_PARTNER_ID
def get_top_selling_items(shop_id, limit=10):
    # 1) ดึงรายการ item_id
    path = "/api/v2/product/get_item_list"
    params = {
        "pagination_offset": 0,
        "pagination_entries_per_page": limit
    }
    resp = call_shopee_api_auto(path, shop_id, params)
    print("DEBUG get_item_list resp:", resp)

    items = resp.get("response", {}).get("item", [])
    if not items:
        return []

    # 2) ดึงรายละเอียด (historical_sold, ชื่อ, ฯลฯ)
    item_ids = [str(i["item_id"]) for i in items]
    path_info = "/api/v2/product/get_item_base_info"
    params_info = {"item_id_list": ",".join(item_ids)}
    detail_resp = call_shopee_api_auto(path_info, shop_id, params_info)
    print("DEBUG get_item_base_info resp:", detail_resp)

    return detail_resp.get("response", {}).get("item_list", [])
def get_item_list(shop_id, page_size=20):
    access_token, refresh_token = get_token(shop_id)
    if not access_token:
        raise ValueError(f"No access_token found for shop_id {shop_id}")

    path = "/api/v2/product/get_item_list"
    timestamp = int(time.time())
    sign = shopee_generate_sign(path, timestamp, access_token, shop_id)

    url = f"{BASE_URL}{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign,
        "access_token": access_token,
        "shop_id": shop_id,
        "page_size": page_size,
    }

    resp = requests.get(url, params=params)
    return resp.json()