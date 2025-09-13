# api/shopee_api.py
import time  # สำหรับ timestamp (ใน call_shopee_api เรียกใช้)
from services.shopee_auth import call_shopee_api_auto # ฟังก์ชัน generic caller
def get_top_selling_items(shop_id, limit=10):
    path = "/api/v2/product/get_item_list"
    params = {
        "offset": 0,
        "page_size": limit
    }
    resp = call_shopee_api_auto(path, shop_id, params)
    items = resp.get("response", {}).get("item", [])

    results = []
    if items:
        # ดึงรายละเอียดสินค้าทีละ item_id
        item_ids = [str(i["item_id"]) for i in items]
        path_info = "/api/v2/product/get_item_base_info"
        params_info = {"item_id_list": ",".join(item_ids)}
        detail_resp = call_shopee_api_auto(path_info, shop_id, params_info)
        results = detail_resp.get("response", {}).get("item_list", [])

    return results

