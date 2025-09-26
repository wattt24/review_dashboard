# services/shopee_auth.py
import os, json
import time, hmac, hashlib, requests, binascii
import urllib.parse
from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_REDIRECT_URI, SHOPEE_PARTNER_KEY, SHOPEE_SHOP_ID)
from utils.token_manager import auto_refresh_token, get_latest_token
from oauth2client.service_account import ServiceAccountCredentials
# Shopee API base URL (อย่าใช้ redirect_uri ตรงนี้)
BASE_URL = "https://partner.shopeemobile.com/api/v2"
BASE_URL_AUTH = "https://partner.shopeemobile.com" 

# ใช้สร้าง URL สำหรับให้ร้านกด authorize โดยไม่ต้องเข้า shopee open platform เอง
def shopee_get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())  # ต้องเป็นวินาที 10 หลัก
    sign = shopee_generate_sign(path, timestamp, is_authorize=True)

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

# สำหรับรับshop_id, code ครั้งแรกเพื่อไปแลก access_token   
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




# จะ refresh แบบ ยังไม่หมดอายุ 
def shopee_refresh_access_token(shop_id: str, refresh_token: str): 
    path = "/api/v2/auth/token/refresh"
    timestamp = int(time.time())

    # ✅ sign ที่ถูกต้อง
    sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        sign_input.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL_AUTH}{path}"
    params = {
        "partner_id": str(SHOPEE_PARTNER_ID),
        "timestamp": str(timestamp),
        "sign": sign
    }

    body = {
        "partner_id": str(SHOPEE_PARTNER_ID),
        "shop_id": int(shop_id),
        "refresh_token": refresh_token  # ❌ ไม่ต้อง decode
    }

    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    return data
