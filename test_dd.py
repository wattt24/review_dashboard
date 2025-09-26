import time, hmac, hashlib, requests
import os, json
import urllib.parse

from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
from utils.token_manager import get_latest_token, auto_refresh_token
BASE_URL = "https://partner.shopeemobile.com"
# ค่าพวกนี้ดึงจาก config หรือ Google Sheet
SHOPEE_PARTNER_ID = 2012650
from utils.config import SHOPEE_PARTNER_SECRET, SHOPEE_PARTNER_ID
BASE_URL = "https://partner.shopeemobile.com"

def shopee_get_shop_info(shop_id, access_token):
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())

    # ✅ base_string สำหรับ sign
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign,
        "access_token": access_token,
        "shop_id": shop_id
    }

    print("BASE STRING:", base_string)
    print("SIGN:", sign)
    print("URL:", url)
    print("PARAMS:", params)

    resp = requests.get(url, params=params, timeout=15)
    return resp.json()


# ทดลองเรียก
shop_id = 57360480
access_token = "7a52646966667a71736f5a6763745973"  # จาก callback/Google Sheet
info = shopee_get_shop_info(shop_id, access_token)
print("== ข้อมูลร้าน ==")
print(info)
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def fetch_items_from_shopee(account_id: int):
    # 1) ดึง token ล่าสุดจาก Google Sheet
    
    token_info = get_latest_token("shopee", account_id)
    if not token_info:
        raise ValueError(f"❌ No token found for shopee:{account_id}")

    access_token = token_info["access_token"]

    # 2) ดึง item list จาก Shopee API
    items = shopee_get_item_list(
        shop_id=account_id,
        access_token=access_token
    )
    return items
# ===== Helper สำหรับดึง token จาก Google Sheet =====
def get_shopee_access_token(shop_id: str, force_refresh: bool = False):
    """
    ดึง access_token จาก Google Sheet และ auto-refresh ถ้าจำเป็น
    """
    token = auto_refresh_token("shopee", shop_id, force=force_refresh)
    if token:
        return token
    # fallback กรณี refresh ไม่สำเร็จ → ดึง token ล่าสุดที่บันทึกไว้
    token_data = get_latest_token("shopee", shop_id)
    return token_data["access_token"] if token_data else None
def shopee_generate_sign(path, timestamp, shop_id, access_token ):
    print("shopee_generate_sign:.............//////")
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
def shopee_get_item_list(shop_id: int, access_token: str, offset=0, page_size=1):
    path = "/api/v2/product/get_item_list"
    timestamp = int(time.time())
    
    # สร้าง sign
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    print("shopee_get_item_list:.............//////")
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}"  # BASE_URL = https://partner.shopeemobile.com
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign,
        "access_token": access_token,
        "shop_id": shop_id,
        "offset": offset,
        "page_size": page_size
    }
    print("BASE STRING:", base_string)
    print("SIGN:", sign)
    print("URL:", url)
    print("PARAMS:", params)
    resp = requests.get(url, params=params, timeout=15)
    return resp.json()

# # ===== ตัวอย่างการเรียกใช้งาน =====
if __name__ == "__main__":
#     # ดึงหมวดหมู่
#     categories = shopee_get_categories(SHOPEE_SHOP_ID)
#     print("== หมวดหมู่ทั้งหมดจาก Shopee ==")
#     #print(json.dumps(categories, indent=2, ensure_ascii=False))#json.dumps = แปลง Python object (dict/list) → string ในรูปแบบ JSON indent=2 = จัด format JSON ให้สวย มีการย่อหน้า (pretty-print) ระดับ 2 space ensure_ascii=False = ให้แสดงตัวอักษร UTF-8 ตามจริง (เช่น ภาษาไทย "หมวดหมู่")
#     # print(type(categories))
#     # print(categories)
    def fetch_items_from_shopee(account_id: int):
    # 1) ดึง token ล่าสุดจาก Google Sheet
        token_info = get_latest_token("shopee", account_id)
        if not token_info:
            raise ValueError(f"❌ No token found for shopee:{account_id}")

        access_token = token_info["access_token"]

        # 2) ดึง item list จาก Shopee API
        items = shopee_get_item_list(
            shop_id=account_id,
            access_token=access_token
        )
        
        return items
    items = fetch_items_from_shopee(SHOPEE_SHOP_ID)
    print("== รายการสินค้าในร้าน ==")
    print(items)
