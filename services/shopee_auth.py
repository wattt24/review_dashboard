# services/shopee_auth.py
import time, hmac, hashlib, requests
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_REDIRECT_URI
)
from utils.token_manager import save_token,auto_refresh_token

# Shopee API base URL (อย่าใช้ redirect_uri ตรงนี้)
BASE_URL = "https://partner.shopeemobile.com"

# ========== SIGN GENERATOR ==========
def generate_sign(path, timestamp, extra_string=""):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{extra_string}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

# ========== STEP 1: Authorization URL ==========
def get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = generate_sign(path, timestamp, SHOPEE_REDIRECT_URI)

    return (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )

# ========== STEP 2: Get Token ==========
def get_token(code: str, shop_id: int):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = generate_sign(path, timestamp)

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
    sign = generate_sign(path, timestamp)

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
    sign = generate_sign(path, timestamp, access_token + str(shop_id))

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )
    resp = requests.get(url, params=params, timeout=30)
    return resp.json()
# ====== Wrapper สำหรับเรียก Shopee API แบบอัตโนมัติ  ======
def call_shopee_api_auto(path, shop_id, params=None):
    # ดึง access_token และต่ออายุให้อัตโนมัติ
    access_token = auto_refresh_token("shopee", shop_id)

    from .shopee_auth import call_shopee_api
    resp = call_shopee_api(path, access_token, shop_id, params)
    return resp