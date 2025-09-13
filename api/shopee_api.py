# api/shopee_api.py
import time  # สำหรับ timestamp (ใน call_shopee_api เรียกใช้)
from services.shopee_auth import call_shopee_api_auto # ฟังก์ชัน generic caller
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
