# import time, hmac, hashlib, requests
# import json

# BASE_URL = "https://partner.shopeemobile.com"
# from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_PARTNER_KEY, SHOPEE_SHOP_ID)

# SHOP_ID = "57360480"
# ACCESS_TOKEN = "7a52646966667a71736f5a6763745973"

# def shopee_get_ratings(shop_id, access_token, offset=0, limit=50):
    
    
#     path = "/api/v2/ratings/get_item_rating"
#     timestamp = int(time.time())
#     body = {
#         "item_id": ITEM_ID,
#         "pagination_offset": 0,
#         "pagination_entries_per_page": 50
#     }
#     body_json = json.dumps(body, separators=(',', ':'))

#     # สร้าง sign
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{body_json}"
#     sign = hmac.new(SHOPEE_PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": access_token,
#         "shop_id": shop_id
#     }

#     res = requests.post(BASE_URL + path, params=params, data=body_json, headers={"Content-Type": "application/json"})
#     print(res.json())
#     print("res",res)
#     print("params",params)
#     print("sign",sign)
#     print("base_string",base_string)
#     return res.json()

# # ==== ตัวอย่างเรียกใช้ ====
# ratings = shopee_get_ratings(SHOP_ID, ACCESS_TOKEN)
# print(json.dumps(ratings, indent=2, ensure_ascii=False))


# import time, hmac, hashlib, requests
# import os, json
# import urllib.parse

# from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
# from utils.token_manager import get_latest_token
# BASE_URL = "https://partner.shopeemobile.com"
# # ค่าพวกนี้ดึงจาก config หรือ Google Sheet
# SHOPEE_PARTNER_ID = 2012650
# from utils.config import SHOPEE_PARTNER_SECRET, SHOPEE_PARTNER_ID
# BASE_URL = "https://partner.shopeemobile.com"

# def shopee_get_shop_info(shop_id, access_token):
#     path = "/api/v2/shop/get_shop_info"
#     timestamp = int(time.time())

#     # ✅ base_string สำหรับ sign
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
#     sign = hmac.new(
#         SHOPEE_PARTNER_SECRET.encode("utf-8"),
#         base_string.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": access_token,
#         "shop_id": shop_id
#     }

#     print("BASE STRING:", base_string)
#     print("SIGN:", sign)
#     print("URL:", url)
#     print("PARAMS:", params)

#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()


# # ทดลองเรียก
# shop_id = 57360480
# access_token = "76686b686b484d794b4f647941534a6f"  # จาก callback/Google Sheet
# info = shopee_get_shop_info(shop_id, access_token)
# print("== ข้อมูลร้าน ==")
# print(info)
# #//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# def fetch_items_from_shopee(account_id: int):
#     # 1) ดึง token ล่าสุดจาก Google Sheet
    
#     token_info = get_latest_token("shopee", account_id)
#     if not token_info:
#         raise ValueError(f"❌ No token found for shopee:{account_id}")

#     access_token = token_info["access_token"]

#     # 2) ดึง item list จาก Shopee API
#     items = shopee_get_item_list(
#         shop_id=account_id,
#         access_token=access_token
#     )
#     return items
# ===== Helper สำหรับดึง token จาก Google Sheet =====



# def shopee_get_item_list(shop_id: int, access_token: str, offset=0, page_size=10):
#     path = "/api/v2/product/get_item_list"
#     timestamp = int(time.time())
    
#     # สร้าง sign
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
#     print("shopee_get_item_list:.............//////")
#     sign = hmac.new(
#         SHOPEE_PARTNER_SECRET.encode("utf-8"),
#         base_string.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": access_token,
#         "shop_id": int(shop_id),  # บังคับ int
#         "offset": offset,
#         "page_size": page_size
#     }
#     print("BASE STRING:", base_string)
#     print("SIGN:", sign)
#     print("URL:", url)
#     print("PARAMS:", params)
#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()


# # # ===== ตัวอย่างการเรียกใช้งาน =====

    # print(json.dumps(categories, indent=2, ensure_ascii=False))#json.dumps = แปลง Python object (dict/list) → string ในรูปแบบ JSON indent=2 = จัด format JSON ให้สวย มีการย่อหน้า (pretty-print) ระดับ 2 space ensure_ascii=False = ให้แสดงตัวอักษร UTF-8 ตามจริง (เช่น ภาษาไทย "หมวดหมู่")
# #     # print(type(categories))
# #     # print(categories)
#     def fetch_items_from_shopee(account_id: int):
#     # 1) ดึง token ล่าสุดจาก Google Sheet
#         token_info = get_latest_token("shopee", account_id)
#         if not token_info:
#             raise ValueError(f"❌ No token found for shopee:{account_id}")

#         access_token = token_info["access_token"]

#         # 2) ดึง item list จาก Shopee API
#         items = shopee_get_item_list(
#             shop_id=account_id,
#             access_token=access_token
#         )
        
#         return items
#     items = fetch_items_from_shopee(SHOPEE_SHOP_ID)
#     print("== รายการสินค้าในร้าน ==")
#     print(items)
# ดึงข้อมูลเฉพาะ platform = fujikathailand
from  database.all_database import get_all_reviews
df_fujika = get_all_reviews(platform="fujikathailand", limit=100)

# แสดงผล
import streamlit as st
st.subheader("📦 รีวิวจาก FujikaThailand")
st.dataframe(df_fujika)
