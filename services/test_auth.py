# services/test_auth.py
import os
import streamlit as st
import time
import json # ต้องแน่ใจว่าได้ import json แล้ว
import hmac
import hashlib
import requests
from datetime import datetime, timedelta, timezone # เพิ่ม timezone ตรงนี้ถ้ายังไม่มี
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_REDIRECT_URI
)

code = os.getenv("CODE")   # code จาก callback ที่ได้ตอน authorize
shop_id = os.getenv("SHOPEE_SHOP_ID")
timestamp = int(time.time())
SANDBOX = True
BASE_URL = "https://partner.test-stable.shopeemobile.com" if SANDBOX else "https://partner.shopeemobile.com"

# ---------------- Google Sheets ----------------
key_path = "/etc/secrets/SERVICE_ACCOUNT_JSON.json"
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # ถ้า st.secrets["SERVICE_ACCOUNT_JSON"] เป็น dict อยู่แล้ว → ไม่ต้อง json.loads
    creds_dict = st.secrets["SERVICE_ACCOUNT_JSON"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1
    return sheet

# ---------------- Shopee OAuth & API ----------------

# แยกฟังก์ชันการ generate signature ตามประเภท API เพื่อความชัดเจนและถูกต้อง
def generate_auth_sign(path, timestamp):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def get_authorization_url():
    """
    Generates the URL for shop authorization (login).
    """
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())

    # Use the specific function for generating auth signature
    sign = generate_auth_sign(path, timestamp)

    # Build the authorization URL
    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )
    return url

def generate_token_sign(path, timestamp, body_dict):
    """
    Generates the signature for /api/v2/auth/token/get
    Base string: partner_id + path + timestamp + request_body(JSON string)
    """
    body_str = json.dumps(body_dict, separators=(',', ':'))  # compact JSON
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{body_str}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest(), body_str


def generate_api_sign(path, timestamp, access_token, shop_id):
    """
    Generates the signature for general Shop API calls (GET/POST with URL params).
    Base string: partner_id + api path + timestamp + access_token + shop_id
    """
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def generate_refresh_sign(path, timestamp, refresh_token_value, shop_id):
    """
    Generates the signature for refresh token API.
    Base string: partner_id + api path + timestamp + refresh_token + shop_id
    """
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{refresh_token_value}{int(shop_id)}" # shop_id ต้องเป็น int ใน base_string
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()


# def get_token(code: str, shop_id: int):
#     path = "/api/v2/auth/token/get"
#     timestamp = int(datetime.now(timezone.utc).timestamp())

#     payload = {
#         "code": code,
#         "shop_id": int(shop_id),
#         "partner_id": int(SHOPEE_PARTNER_ID)
#     }
#     partner_key_bytes = bytes.fromhex(SHOPEE_PARTNER_SECRET[4:])
    
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{code}{int(shop_id)}"
#     sign = hmac.new(
#         partner_key_bytes, base_string.encode("utf-8"), 
#         hashlib.sha256
#     ).hexdigest()


#     url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"

#     resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

#     print("==== DEBUG ====")
#     print("partner_id:", SHOPEE_PARTNER_ID)
#     print("shop_id:", shop_id, type(shop_id))
#     print("code:", code)
#     print("base_string:", base_string)
#     print("sign:", sign)
#     print("url:", url)
#     print("payload:", payload)
#     print("response:", resp.text)
#     print("secret length:", len(SHOPEE_PARTNER_SECRET))
#     print("secret repr:", repr(SHOPEE_PARTNER_SECRET))
#     print("base_string:", base_string)
#     print("sign:", sign)
#     return resp.json()

def get_token(code, shop_id):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())

    # ใช้ key ตรงๆ ไม่ต้อง fromhex
    partner_key_bytes = bytes.fromhex(SHOPEE_PARTNER_SECRET)

    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(partner_key_bytes, base_string.encode("utf-8"), hashlib.sha256).hexdigest()

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"

    payload = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }

    print("==== DEBUG ====")
    print("partner_id:", SHOPEE_PARTNER_ID)
    print("shop_id:", shop_id, type(shop_id))
    print("code:", code)
    print("base_string:", base_string)
    print("sign:", sign)
    print("url:", url)
    print("payload:", payload)
    print("secret repr:", repr(SHOPEE_PARTNER_SECRET))  # 🧪 debug ดูค่า key จริง

    resp = requests.post(url, json=payload)
    print("response:", resp.text)
    print("==== DEBUG ====")

    return resp.json()

def refresh_token(refresh_token_value, shop_id):
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())

    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{refresh_token_value}{int(shop_id)}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token_value,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }
    r = requests.post(url, json=payload)
    return r.json()

def save_token(shop_id, access_token, refresh_token_value, expires_in, refresh_expires_in):
    sheet = get_sheet()  # เรียก function ก่อนใช้

    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat()

    try:
        # ใช้ str(shop_id) เพื่อค้นหาในชีต
        cell = sheet.find(str(shop_id))
        row = cell.row
        sheet.update(f"B{row}:E{row}", [[access_token, refresh_token_value, expired_at, refresh_expired_at]])
        sheet.update(f"F{row}", datetime.now().isoformat())
    except gspread.exceptions.CellNotFound:
        sheet.append_row([shop_id, access_token, refresh_token_value, expired_at, refresh_expired_at, datetime.now().isoformat()])


def get_latest_token(shop_id):
    sheet = get_sheet()  # เรียก function ก่อนใช้

    records = sheet.get_all_records()
    for record in records:
        if str(record["shop_id"]) == str(shop_id):
            return {
                "access_token": record["access_token"],
                "refresh_token": record["refresh_token"],
                "expired_at": record["expired_at"],
                "refresh_expired_at": record["refresh_expired_at"]
            }
    return None

def get_valid_access_token(shop_id):
    token = get_latest_token(shop_id)
    if not token:
        return None

    expired_at = datetime.fromisoformat(token["expired_at"])
    refresh_expired_at = datetime.fromisoformat(token["refresh_expired_at"])

    if datetime.now() >= expired_at and datetime.now() < refresh_expired_at:
        new_tokens = refresh_token(token["refresh_token"], shop_id)
        if "access_token" in new_tokens:
            save_token(
                shop_id,
                new_tokens["access_token"],
                new_tokens["refresh_token"],
                new_tokens["expires_in"],
                new_tokens["refresh_expires_in"]
            )
            return new_tokens["access_token"]
        else:
            return None
    elif datetime.now() < expired_at:
        return token["access_token"]
    else:
        return None
def call_shopee_api(path, shop_id, access_token, method="GET", payload=None):
    """
    Generic function to call Shopee Shop API
    """
    timestamp = int(time.time())
    sign = generate_api_sign(path, timestamp, access_token, shop_id)

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={shop_id}"
        f"&sign={sign}"
    )

    headers = {"Content-Type": "application/json"}

    if method.upper() == "POST":
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"})

    else:
        resp = requests.get(url, headers=headers, params=payload or {})

    print("==== DEBUG call_shopee_api ====")
    print("URL:", url)
    print("Payload:", payload)
    print("Response:", resp.text)
    
    return resp.json()
