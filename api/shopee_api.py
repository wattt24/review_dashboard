# shopee_api.py
import time  # สำหรับ timestamp (ใน call_shopee_api เรียกใช้)
from services.shopee_auth import call_shopee_api_auto # ฟังก์ชัน generic caller
def get_top_selling_items(shop_id, limit=10):
    path = "/api/v2/product/get_item_list"
    params = {
        "pagination_offset": 0,
        "pagination_entries_per_page": limit
    }
    resp = call_shopee_api_auto(path, shop_id, params)
    return resp.get("items", [])
