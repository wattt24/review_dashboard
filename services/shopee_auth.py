# services/shopee_auth.py
import time, hmac, hashlib, requests
import urllib.parse
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_REDIRECT_URI
)
import json
from utils.token_manager import save_token
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import time, hmac, hashlib, requests
from fastapi import APIRouter, Request
# router = APIRouter()
# Shopee API base URL (อย่าใช้ redirect_uri ตรงนี้)
# BASE_URL = "https://partner.shopeemobile.com"
BASE_URL = "https://partner.shopeemobile.com/api/v2"
BASE_URL_AUTH = "https://partner.shopeemobile.com"  
# ========== SIGN GENERATOR ==========
import time, hmac, hashlib
# ===== Google Sheet Setup =====
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
def shopee_get_gspread_client(service_account_json_path=None):
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_json_path, scope)
    return gspread.authorize(creds)

# ใช้สร้าง URL สำหรับให้ร้านกด authorize โดยไม่ต้องเข้า shopee open platform เอง
def shopee_get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())  # ต้องเป็นวินาที 10 หลัก
    sign = shopee_generate_sign(path, timestamp, is_authorize=True)

    redirect_encoded = urllib.parse.quote(SHOPEE_REDIRECT_URI, safe='')

    url = (
        f"{BASE_URL_AUTH}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={redirect_encoded}"
    )
    return url

# ถูกเรียก ภายใน shopee_get_access_token() และ auth_partner()ไม่ได้เรียกโดยตรงจาก callback
def shopee_generate_sign(path, timestamp, code=None, shop_id=None, is_authorize=False):
    message = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    # ✅ ตอนแลก token ต้องใส่ code+shop_id
    if code and shop_id:
        message += f"{code}{shop_id}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return sign
# 1️⃣ ตรวจสอบร้านพาร์ทเนอร์
def auth_partner(shop_id):
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = shopee_generate_sign(path, timestamp, shop_id=shop_id)
    
    url = f"{BASE_URL}{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id,
        "timestamp": timestamp,
        "sign": sign
    }
    response = requests.get(url, params=params)
    return response.json()

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


# ===== ดึงข้อมูลจาก Google Sheet และเรียก API =====
def process_shopee_tokens(sheet_key, service_account_json_path=None):
    client = shopee_get_gspread_client(service_account_json_path)
    sheet = client.open_by_key(sheet_key).sheet1
    records = sheet.get_all_records()

    for idx, row in enumerate(records, start=2):
        platform = row.get("platform", "").lower()
        shop_id = str(row.get("account_id", "")).strip()
        code = row.get("code", "").strip()  # สมมติว่าเก็บ code ไว้ใน sheet

        if platform != "shopee" or not shop_id or not code:
            continue

        # 1️⃣ ตรวจสอบร้าน
        partner_info = auth_partner(shop_id)
        print(f"[{shop_id}] Partner info:", partner_info)

        # 2️⃣ แลก access token
        token_data = shopee_get_access_token(shop_id, code)
        print(f"[{shop_id}] Token data:", token_data)

        if token_data and "access_token" in token_data:
            save_token(
                "shopee",
                shop_id,
                token_data["access_token"],
                token_data.get("refresh_token", ""),
                token_data.get("expire_in", 0),
                token_data.get("refresh_expires_in", 0)
            )




