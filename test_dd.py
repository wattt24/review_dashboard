# import requests
# import time
# import hmac
# import hashlib

# # ข้อมูล Partner ของคุณ
# partner_id = "2012650"
# partner_key = "shk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
# access_token = "486252474772656e5a644355724d5a6e"
# shop_id = 57360480

# path = "/api/v1/items/get"

# def generate_sign(partner_id, path, timestamp, partner_key):
#     string_to_sign = f"{partner_id}{path}{timestamp}{access_token}"
#     sign = hmac.new(partner_key.encode(), string_to_sign.encode(), hashlib.sha256).hexdigest()
#     return sign

# def get_items(shop_id, offset=0, page_size=50):
#     timestamp = int(time.time())
#     sign = generate_sign(partner_id, path, timestamp, partner_key)

#     url = f"https://partner.shopeemobile.com{path}"

#     payload = {
#         "shop_id": shop_id,
#         "pagination_offset": offset,
#         "pagination_entries_per_page": page_size
#     }

#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": access_token,
#         "X-Shopee-Signature": sign
#     }

#     response = requests.post(url, json=payload, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Error:", response.status_code, response.text)
#         return None

# # ลองดึงหน้าต้น 50 รายการ
# data = get_items(shop_id, offset=0, page_size=50)

# if data and "items" in data:
#     for item in data["items"]:
#         print(f"Item ID: {item['item_id']}, Name: {item['name']}, Price: {item['price']}")
# else:
#     print("No items found or API error")

#test_categories.py
from services.shopee_auth import shopee_get_categories
from utils.config import SHOPEE_SHOP_ID #57360480
import json
access_token = "76784948454a4b76506c4e696b717a44"

categories = shopee_get_categories(access_token, SHOPEE_SHOP_ID)
# แสดงผลลัพธ์
print("== หมวดหมู่จาก Shopee ==")
print(json.dumps(categories, indent=2, ensure_ascii=False))
for cat in categories.get("category_list", []):
    category_id = cat.get("category_id", "ไม่มี ID")
    category_name = cat.get("category_name", "ไม่มีชื่อหมวดหมู่")
    print(f"{category_id}: {category_name}")
    

