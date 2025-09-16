# services/shopee_auth.py
import time, hmac, hashlib, requests
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_REDIRECT_URI
)
from utils.token_manager import save_token,auto_refresh_token
import urllib.parse
redirect = urllib.parse.quote(SHOPEE_REDIRECT_URI)

# Shopee API base URL (อย่าใช้ redirect_uri ตรงนี้)
BASE_URL = "https://partner.shopeemobile.com/api/v2"

# ========== SIGN GENERATOR ==========
import urllib.parse
import time, hmac, hashlib

import urllib.parse
import time, hmac, hashlib

def shopee_generate_sign(path, timestamp, body=""):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{body}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def shopee_get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())

    # ✅ full redirect url (callback ของคุณ)
    redirect_full = SHOPEE_REDIRECT_URI.rstrip("/") + "/shopee/callback"

    # ❌ ไม่ต้องใส่ redirect_full ใน base_string
    sign = shopee_generate_sign(path, timestamp)

    # ✅ encode redirect URI ให้ Shopee รับได้
    redirect_encoded = urllib.parse.quote(redirect_full, safe='')

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
    )
    return url

# ========== STEP 2: Get Token ==========
def get_token(code: str, shop_id: int):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = shopee_generate_sign(path, timestamp)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "code": code,
        "shop_id": shop_id,
        "partner_id": SHOPEE_PARTNER_ID,
    }

    resp = requests.post(url, json=payload, timeout=30)
    data = resp.json()
    print("=== Shopee get_token response ===")
    print(data)
    # ตรวจสอบ error ก่อน
    if data.get("error"):
        raise ValueError(
            f"Shopee API Error: {data.get('error')} - {data.get('message', '')} | full_response={data}"
        )
    print("Shopee token response:", data)
    # save token
    save_token(
        "shopee", shop_id,
        data["access_token"], 
        data["refresh_token"],
        data.get("expire_in", 0),          # ใช้ expire_in แทน expires_in
        data.get("refresh_expires_in", 0)  # อาจไม่มี ให้ default=0
    )

    return data


# ========== STEP 3: Refresh Token ==========
def refresh_token(refresh_token_value, shop_id):
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = shopee_generate_sign(path, timestamp)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token_value,
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id
    }

    resp = requests.post(url, json=payload, timeout=30)
    return resp.json()

# ========== STEP 4: Call Shopee API ==========
def call_shopee_api(path, access_token, shop_id, params=None):
    timestamp = int(time.time())

    # path ที่ใช้ sign ต้องรวม /api/v2
    sign_path = "/api/v2" + path if not path.startswith("/api/v2") else path
    sign = shopee_generate_sign(sign_path, timestamp, access_token + str(shop_id))

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )
    print("👉 Shopee request URL:", url)  # debug
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()

# ====== Wrapper สำหรับเรียก Shopee API แบบอัตโนมัติ  ======
def call_shopee_api_auto(path, shop_id, params=None):
    # ถ้า shop_id เป็น dict ให้ดึงค่าออก
    if isinstance(shop_id, dict):
        shop_id = shop_id.get("shop_id")
    shop_id = int(shop_id)
    
    access_token = auto_refresh_token("shopee", shop_id)
    if not access_token:
        auth_url = shopee_get_authorization_url()
        raise RuntimeError(f"❌ ไม่มี access_token สำหรับร้าน {shop_id}.\n{auth_url}")

    resp = call_shopee_api(path, access_token, shop_id, params)
    if resp and resp.get("error") == 10008:
        access_token = auto_refresh_token("shopee", shop_id)
        if not access_token:
            raise RuntimeError("❌ ไม่สามารถต่ออายุ access_token ได้ — กรุณา authorize ใหม่")
        resp = call_shopee_api(path, access_token, shop_id, params)
    return resp

def check_shop_type(shop_id: int):
    """
    ตรวจสอบประเภทร้านและสถานะร้าน
    คืนค่า dict เช่น:
    {
        "shop_name": "FUJIKA Official",
        "is_sip": False,
        "status": "NORMAL",
        "shop_fulfillment_flag": "Others"
    }
    """
    try:
        if isinstance(shop_id, dict):
            shop_id = shop_id.get("shop_id")

        shop_info = call_shopee_api_auto("/api/v2/shop/get_shop_info", shop_id)
        return {
            "shop_name": shop_info.get("shop_name"),
            "is_sip": shop_info.get("is_sip"),
            "status": shop_info.get("status"),
            "shop_fulfillment_flag": shop_info.get("shop_fulfillment_flag"),
        }
    except Exception as e:
        return {"error": str(e)}