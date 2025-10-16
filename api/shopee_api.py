# api/shopee_api.py
import os, json
import datetime
import time, hmac, hashlib, requests
import urllib.parse
from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
from utils.token_manager import get_latest_token, get_latest_token

# ===== Helper สำหรับดึง token จาก Google Sheet =====
def get_shopee_access_token(shop_id: str, force_refresh: bool = False):
    """
    ดึง access_token จาก Google Sheet และ auto-refresh ถ้าจำเป็น
    """
    token = get_latest_token("shopee", shop_id)
    if token:
        return token
    # fallback กรณี refresh ไม่สำเร็จ → ดึง token ล่าสุดที่บันทึกไว้
    token_data = get_latest_token("shopee", shop_id)
    return token_data["access_token"] if token_data else None
def shopee_generate_sign(path, timestamp, shop_id, access_token ):
    print(">>> DEBUG shop_id param:", shop_id)
    print(">>> DEBUG access_token param:", access_token)
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
  
    print("BASE STRING:", base_string)
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    print("BASE STRING:", base_string)
    print("GENERATED SIGN:", sign)  # ดู sign ที่สร้าง
    return sign
# ใช้เรียกดูรายละเอียดร้านได้แล้ว
def get_shopee_shop_info(shop_id, access_token): #    shop_info = get_shopee_shop_info(shop_id, access_token) 
    """
    ดึงข้อมูลร้านจาก Shopee API
    """
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())

    # สร้าง sign
    sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

    # ประกอบ URL เรียก API
    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?access_token={access_token}"
        f"&partner_id={SHOPEE_PARTNER_ID}"
        f"&shop_id={shop_id}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )

    print("🔹 Base string:", f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}")
    print("🔹 Sign:", sign)
    print("🔹 URL:", url)
    print("🔹 Timestamp:", timestamp)
    print("🔹 Human time:", datetime.datetime.fromtimestamp(timestamp))

    # เรียก API
    response = requests.get(url)
    data = response.json()

    print("\n📦 Shopee Shop Info Response:")
    print(data)

    return data
# ใช้ได้ เรียกดู global ของ Shopee
def shopee_get_categories(shop_id, language="en"):
    path = "/api/v2/product/get_category"
    base_url = "https://partner.shopeemobile.com"
    timestamp = int(time.time())

    token_data = get_latest_token("shopee", shop_id)
    if not token_data:
        raise ValueError("❌ ไม่พบ Shopee access_token")
    access_token = token_data["access_token"]

    shop_id = int(shop_id)
    sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign,
        "language": language
    }

    url = f"{base_url}{path}"
    response = requests.get(url, params=params)
    return response.json()

# ยังใช้ไม่ได้ ค่าว่าง
def shopee_get_item_list(shop_id, access_token, page_size=100, offset=0):
    path = "/api/v2/product/get_item_list"
    timestamp = int(time.time())

    access_token = get_shopee_access_token(shop_id)
    if not access_token:
        raise ValueError("❌ ไม่พบ Shopee access_token")
    
    sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

    url = f"https://partner.shopeemobile.com{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign,
        "pagination_offset": offset,
        "pagination_entries_per_page": page_size
    }

    resp = requests.get(url, params=params)
    return resp.json()


# ===== ตัวอย่างการเรียกใช้งาน =====
if __name__ == "__main__":
    # ดึงหมวดหมู่
    categories = shopee_get_categories(SHOPEE_SHOP_ID)
    print("== หมวดหมู่ทั้งหมดจาก Shopee ==")
    print(json.dumps(categories, indent=2, ensure_ascii=False))

    all_categories = categories.get("category_list", [])
    category_map = {
        cat["category_id"]: cat.get("display_category_name", "ไม่มีชื่อหมวดหมู่")
        for cat in all_categories
    }

    # ดึงสินค้าทั้งหมดในร้าน
    all_category_ids = set()
    offset = 0
    page_size = 100

    while True:
        data = shopee_get_item_list(SHOPEE_SHOP_ID, page_size, offset)
        items = data.get("items", [])

        if not items:
            break

        for item in items:
            all_category_ids.add(item["category_id"])

        offset += page_size

    print("== Category IDs ของสินค้าร้านเรา ==")
    print(all_category_ids)

    category_names_in_shop = [
        category_map.get(cat_id, "ไม่พบหมวดหมู่")
        for cat_id in all_category_ids
    ]

    print("== หมวดที่ร้านเรามี ==")
    for name in category_names_in_shop:
        print(name)