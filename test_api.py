# test_api.py
from services.test_auth import call_shopee_api, get_valid_access_token
from utils.config import SHOPEE_SHOP_ID

# ดึง token ที่ valid
access_token = get_valid_access_token(SHOPEE_SHOP_ID)
if not access_token:
    print("ยังไม่มี access token หรือ token หมดอายุ")
else:
    # 1. เพิ่มสินค้า
    add_item_payload = {
        "item_name": "Test Product",
        "description": "This is a test product",
        "price": 100.0,
        "stock": 10
    }
    resp = call_shopee_api("item/add_item", access_token, SHOPEE_SHOP_ID, params=add_item_payload)
    print("Add Item Response:", resp)

    # 2. ดึงคำสั่งซื้อ
    get_order_payload = {"page_size": 5, "pagination_offset": 0}
    resp = call_shopee_api("orders/get_order_list", access_token, SHOPEE_SHOP_ID, params=get_order_payload)
    print("Get Order Response:", resp)

    # 3. เช็ก stock / price
    get_item_payload = {"item_id": 123456789}  # ใส่ Item ID จริง
    resp = call_shopee_api("item/get_item_base", access_token, SHOPEE_SHOP_ID, params=get_item_payload)
    print("Get Item Response:", resp)
