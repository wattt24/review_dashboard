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

# ====== สร้าง URL สำหรับร้านกด authorize ======
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

def shopee_get_gspread_client(service_account_json_path=None):
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_json_path, scope)
    return gspread.authorize(creds)

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
    """
    แลก Authorization Code เพื่อรับ Access Token และ Refresh Token จาก Shopee API.
    
    Args:
        shop_id (int): Shop ID ที่ได้จาก Shopee callback
        code (str): Authorization code ที่ได้จาก Shopee callback
        
    Returns:
        dict: response จาก Shopee API ที่มี access_token และ refresh_token
        
    Raises:
        ValueError: หาก Shopee API คืนค่า error กลับมา
    """
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time()) # ใช้ timestamp ณ เวลาปัจจุบัน
    
    # Shopee V2 API ต้องการ JSON payload ใน body สำหรับ endpoint นี้
    # และใช้ JSON string นี้ในการสร้าง signature
    body = {
        "shop_id": int(shop_id),
        "code": code,
        "partner_id": SHOPEE_PARTNER_ID
    }
    
    # NOTE: การเรียงลำดับคีย์ใน JSON string มีผลต่อการคำนวณ sign
    # Shopee ต้องการให้เรียงตามตัวอักษรของคีย์: "code", "partner_id", "shop_id"
    # แต่ในกรณีนี้เราจะใช้ JSON.dumps ที่เรียงลำดับให้แล้ว (ถ้า key เป็น string)
    # หรือเราสามารถสร้าง string เองเพื่อให้แน่ใจว่าถูกต้อง
    body_json_string = json.dumps(body)

    # 1. สร้าง String ที่จะใช้ในการ Sign ตามที่ Shopee กำหนด:
    #    "partner_id" + "path" + "timestamp" + "JSON_body"
    #    JSON_body คือ String ที่เกิดจาก json.dumps(body)
    sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{body_json_string}"

    # 2. คำนวณ HMAC-SHA256 signature
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        sign_input.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    # 3. กำหนด URL พร้อม Query Parameters (partner_id, timestamp, sign)
    #    ส่วน body จะถูกส่งไปใน POST request
    url = f"{BASE_URL_AUTH}{path}"
    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "sign": sign
    }

    print("=== DEBUG Shopee Access Token ===")
    print("Sign Input:", sign_input)
    print("Generated Sign:", sign)
    print("Final URL (with query params):", url)
    print("JSON Body:", body)
    print("===============================")

    # 4. ส่ง POST Request ไปยัง Shopee API
    #    ใช้ `json=body` เพื่อให้ requests จัดการแปลง body เป็น JSON string
    #    และตั้ง Content-Type เป็น application/json โดยอัตโนมัติ
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()

    print("=== DEBUG Response ===")
    print(data)
    print("=====================")

    if data.get("error"):
        raise ValueError(f"Shopee API Error: {data.get('error')} - {data.get('message')}")

    return data

# def shopee_get_access_token(shop_id, code):
#     path = "/api/v2/auth/token/get"   # ← ต้องเป็น token/get
#     timestamp = int(time.time())

#     shop_id_str = str(shop_id)
#     code_str = str(code)

#     sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{code_str}{shop_id_str}"
#     sign = hmac.new(
#         SHOPEE_PARTNER_SECRET.encode("utf-8"),
#         sign_input.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

#     url = f"{BASE_URL_AUTH}{path}"
#     params = {
#         "partner_id": SHOPEE_PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign
#     }
#     body = {
#         "code": code_str,
#         "shop_id": shop_id_str
#     }

#     resp = requests.post(url, params=params, json=body, timeout=30)
#     data = resp.json()

#     if data.get("error"):
#         raise ValueError(f"Shopee API Error: {data.get('error')} - {data.get('message')}")

#     return data


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
# @router.get("/shopee/callback")
# async def shopee_callback(request: Request):
#     code = request.query_params.get("code")
#     shop_id = request.query_params.get("shop_id")
#     timestamp = int(time.time())
#     path = "/api/v2/auth/token/get"

#     # sign ตาม doc
#     sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{code}{shop_id}"
#     sign = hmac.new(
#         SHOPEE_PARTNER_SECRET.encode("utf-8"),
#         sign_input.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

#     url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"

#     payload = {
#         "code": code,
#         "shop_id": int(shop_id)
#     }

#     print("=== DEBUG Shopee Access Token ===")
#     print("Partner ID:", SHOPEE_PARTNER_ID)
#     print("Shop ID:", shop_id)
#     print("Code:", code)
#     print("Timestamp:", timestamp)
#     print("Sign Input String:", sign_input)
#     print("Generated Sign:", sign)
#     print("Request URL:", url)
#     print("Request Payload:", payload)
#     print("================================")

#     resp = requests.post(url, json=payload)
#     print("=== DEBUG Shopee Response ===")
#     print(resp.json())
#     print("=============================")

#     return resp.json()




