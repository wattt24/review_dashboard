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
    try:
        service_json = st.secrets["SERVICE_ACCOUNT_JSON"]
    except KeyError:
        st.error("❌ 'SERVICE_ACCOUNT_JSON' not found in st.secrets")
        st.write("🧪 Available keys:", list(st.secrets.keys()))
        st.stop()

    sheet_id = st.secrets["GOOGLE_SHEET_ID"]

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(service_json),
        scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

# ---------------- Shopee OAuth & API ----------------

# แยกฟังก์ชันการ generate signature ตามประเภท API เพื่อความชัดเจนและถูกต้อง
def generate_auth_sign(path, timestamp):
    """
    Generates the signature for the initial authorization URL.
    Base string: partner_id + api path + timestamp
    """
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

# *** แก้ไข get_token() ตรงนี้ ***
import time
import hmac
import hashlib
import requests
from datetime import datetime, timezone

def get_token(code: str, shop_id: int):
    path = "/api/v2/auth/token/get"
    timestamp = int(datetime.now(timezone.utc).timestamp())

    # Shopee spec: base_string = partner_id + path + timestamp + code + shop_id
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{code}{shop_id}"

    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),  # ✅ ใช้ SECRET เป็น key
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"

    payload = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": SHOPEE_PARTNER_ID
    }

    resp = requests.post(url, json=payload)

    print("==== DEBUG ====")
    print("UTC Timestamp:", timestamp)
    print("URL:", url)
    print("Payload:", payload)
    print("Base String:", base_string)
    print("Sign:", sign)
    print("Response:", resp.text)

    return resp.json()

def refresh_token(refresh_token_value, shop_id):
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    
    payload = {
        "refresh_token": refresh_token_value,
        "shop_id": int(shop_id) # ต้องเป็น int
    }
    # สำหรับ refresh token API, payload ก็ต้องถูกรวมใน base_string ด้วย
    sorted_payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{sorted_payload_json}"

    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    r = requests.post(url, json=payload)
    return r.json()

def call_shopee_api(path, access_token, shop_id, params=None):
    timestamp = int(time.time())
    sign = generate_api_sign(path, timestamp, access_token, shop_id)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}"
    r = requests.get(url, params=params)
    return r.json()

# ---------------- Google Sheets token management ----------------
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