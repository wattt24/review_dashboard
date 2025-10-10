# services/shopee_auth.py
import os, json, datetime 
import time, hmac, hashlib, requests, binascii
import urllib.parse
from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_REDIRECT_URI, SHOPEE_PARTNER_KEY, SHOPEE_SHOP_ID)
from utils.token_manager import get_latest_token, save_token
# Shopee API base URL (อย่าใช้ redirect_uri ตรงนี้)
BASE_URL = "https://partner.shopeemobile.com/api/v2"
BASE_URL_AUTH = "https://partner.shopeemobile.com" 

def shopee_generate_sign_authorize(path, timestamp):
    """
    สร้าง sign สำหรับ URL authorize
    """
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return sign

def shopee_get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = shopee_generate_sign_authorize(path, timestamp)

    redirect_encoded = urllib.parse.quote(SHOPEE_REDIRECT_URI, safe='')
    scope = "read_item,write_item"

    url = (
        f"{BASE_URL_AUTH}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
        f"&scope={scope}"
    )
    return url
  
def shopee_get_access_token(shop_id, code):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    
    sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"  # ✅ ไม่มี body
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        sign_input.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL_AUTH}{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }

    body = {
        "shop_id": int(shop_id),
        "code": code,
        "partner_id": SHOPEE_PARTNER_ID
    }

    print("Sign Input:", sign_input)
    print("Generated Sign:", sign)
    print("Final URL:", url)
    print("JSON Body:", body)

    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    print("=== DEBUG Response ===")
    print(data)
    print("=====================")

    if data.get("error"):
        raise ValueError(f"Shopee API Error: {data.get('error')} - {data.get('message')}")

    return data

# ถูกเรียก ภายใน shopee_get_access_token() และ auth_partner()ไม่ได้เรียกโดยตรงจาก callback
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

# 1️⃣ ตรวจสอบร้านพาร์ทเนอร์
def auth_partner(shop_id):
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = shopee_generate_sign(path, timestamp, shop_id=shop_id)
    
    url = f"{BASE_URL}{path}"
    params = {
        "partner_id": str(SHOPEE_PARTNER_ID),
        "shop_id": shop_id,
        "timestamp": timestamp,
        "sign": sign
    }
    response = requests.get(url, params=params)
    return response.json()


def get_shopee_refresh_access_token():
    """
    ขอ Access Token ใหม่จาก Shopee Partner API และบันทึกลง Google Sheet
    """
    # ===== ดึง refresh_token ล่าสุดจาก Google Sheet =====
    token_data = get_latest_token(platform="Shopee", account_id=SHOPEE_SHOP_ID)
    if not token_data or not token_data.get("refresh_token"):
        print(f"❌ No refresh_token found for Shopee shop {SHOPEE_SHOP_ID} in Google Sheet")
        return None
    SHOPEE_REFRESH_TOKEN = token_data["refresh_token"]
    timestamp = int(time.time())
    path = "/api/v2/auth/access_token/get"
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(SHOPEE_PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    body = {
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": SHOPEE_SHOP_ID,
        "refresh_token": SHOPEE_REFRESH_TOKEN
    }

    # ===== DEBUG LOG =====
    request_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone(datetime.timedelta(hours=7)))
    print("\n================ Shopee API Debug Info ================")
    print(f"🔹 API Name: {path}")
    print(f"🔹 Full Request URL: {url}")
    print(f"🔹 Request Time (TH timezone): {request_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🔹 Partner ID: {SHOPEE_PARTNER_ID}")
    print(f"🔹 Shop ID: {SHOPEE_SHOP_ID}")
    print(f"🔹 Request Parameters: {body}")
    print("=======================================================\n")

    # ===== ส่ง Request =====
    try:
        response = requests.post(url, json=body, timeout=15)
        data = response.json()
    except Exception as e:
        print("❌ Request failed:", e)
        return None

    # ===== LOG ผลลัพธ์ =====
    print("🟢 Response:")
    print(data)
    if "request_id" in data:
        print(f"🔸 Request ID: {data['request_id']}")
    print("\n=======================================================\n")

    # ===== บันทึกลง Google Sheet =====
    if data.get("access_token") and data.get("refresh_token"):
        expires_in = data.get("expires_in")  # คำนวณเวลาหมดอายุ Access Token
        save_token(
            platform="Shopee",
            account_id=SHOPEE_SHOP_ID,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=expires_in
        )
        print(f"✅ Shopee token saved to Google Sheet for shop {SHOPEE_SHOP_ID}")

    return data