import time
import hmac
import hashlib
import requests
import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta, timezone

from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_KEY,      # Sandbox ใช้ค่า key ที่ขึ้นต้นด้วย shpk...
    SHOPEE_PARTNER_SECRET,   # Production ใช้ secret จริง
    SHOPEE_REDIRECT_URI,
)

# ---------------- Config ----------------
SANDBOX = True
BASE_URL = "https://partner.test-stable.shopeemobile.com" if SANDBOX else "https://partner.shopeemobile.com"

# ---------------- Google Sheets ----------------
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = st.secrets["SERVICE_ACCOUNT_JSON"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1
    return sheet

# ---------------- Signature Utils ----------------
def generate_sign(base_string: str, use_secret=False) -> str:
    key = SHOPEE_PARTNER_SECRET if use_secret else SHOPEE_PARTNER_KEY
    if not key:
        raise ValueError("Missing Shopee Partner Key/Secret")
    return hmac.new(
        key.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def generate_auth_sign(path, timestamp):
    return generate_sign(f"{SHOPEE_PARTNER_ID}{path}{timestamp}")

def generate_token_sign(path, timestamp):
    return generate_sign(f"{SHOPEE_PARTNER_ID}{path}{timestamp}")

def generate_refresh_sign(path, timestamp, refresh_token_value, shop_id):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{refresh_token_value}{int(shop_id)}"
    return generate_sign(base_string)

def generate_api_sign(path, timestamp, access_token, shop_id):
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{int(shop_id)}"
    return generate_sign(base_string)

# ---------------- OAuth Flow ----------------
def get_authorization_url():
    """
    Step 1: สร้าง URL ให้ร้าน authorize
    """
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = generate_auth_sign(path, timestamp)

    return (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )

def get_token(code, shop_id):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    base_string = f"{int(SHOPEE_PARTNER_ID)}{path}{timestamp}"
    # Sandbox: ใช้ partner_key ไม่ใช่ partner_secret
    sign = generate_sign(base_string, use_secret=False)  
    
    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={int(SHOPEE_PARTNER_ID)}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )
    payload = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }
    resp = requests.post(url, json=payload)
    print("==== DEBUG get_token ====")
    print("base_string:", base_string)
    print("sign:", sign)
    print("url:", url)
    print("payload:", payload)
    print("response:", resp.text)
    print("==== DEBUG SIGN ====")
    print("partner_id:", SHOPEE_PARTNER_ID)
    print("path:", path)
    print("timestamp:", timestamp)
    print("base_string:", base_string)
    print("key used:", SHOPEE_PARTNER_KEY)   # ต้องเป็น shpk_xxx
    print("sign:", sign)
    return resp.json()


def refresh_token(refresh_token_value, shop_id):
    """
    Step 3: ใช้ refresh_token แลก access_token ใหม่
    """
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = generate_refresh_sign(path, timestamp, refresh_token_value, shop_id)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token_value,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID),
    }

    resp = requests.post(url, json=payload)
    print("==== DEBUG refresh_token ====")
    print("payload:", payload)
    print("response:", resp.text)
    return resp.json()

# ---------------- Generic API Call ----------------
def call_shopee_api(path, shop_id, access_token, method="GET", payload=None):
    """
    ใช้เรียก Shopee Shop API ทั่วไป
    """
    timestamp = int(time.time())
    sign = generate_api_sign(path, timestamp, access_token, shop_id)

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={int(shop_id)}"
        f"&sign={sign}"
    )

    headers = {"Content-Type": "application/json"}
    if method.upper() == "POST":
        resp = requests.post(url, json=payload, headers=headers)
    else:
        resp = requests.get(url, headers=headers, params=payload or {})

    print("==== DEBUG call_shopee_api ====")
    print("URL:", url)
    print("Payload:", payload)
    print("Response:", resp.text)
    return resp.json()

# ---------------- Token Persistence ----------------
def save_token(platform, account_id, access_token, refresh_token_value, expires_in, refresh_expires_in):
    """
    บันทึก token ลง Google Sheet
    """
    sheet = get_sheet()
    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat() if refresh_expires_in else ""

    try:
        cell = sheet.find(str(account_id))
        row = cell.row
        sheet.update(
            f"A{row}:F{row}",
            [[platform, account_id, access_token, refresh_token_value, expired_at, refresh_expired_at]],
        )
        sheet.update(f"G{row}", datetime.now().isoformat())
    except gspread.exceptions.CellNotFound:
        sheet.append_row([
            platform, account_id, access_token, refresh_token_value,
            expired_at, refresh_expired_at, datetime.now().isoformat()
        ])
