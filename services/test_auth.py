# services/test_auth.py
import os
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

# ---------------- Google Sheets ----------------
key_path = "/etc/secrets/service_account.json"
#key_path = "data/service_account.json"

# เพิ่มส่วนนี้เข้าไป
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
# สิ้นสุดส่วนที่ต้องเพิ่ม


# ---------------- Config toggle ----------------
SANDBOX = True
BASE_URL = "https://partner.test-stable.shopeemobile.com" if SANDBOX else "https://partner.shopeemobile.com"

# ---------------- Google Sheets ----------------
key_path = "/etc/secrets/service_account.json"
#key_path = "data/service_account.json" # ถ้าใช้ local path ให้ comment บรรทัดบนแล้วใช้บรรทัดนี้แทน

# **** สำคัญ: ตรวจสอบว่าคุณตั้งค่า Environment Variable 'SERVICE_ACCOUNT_KEY_PATH' บน Render แล้ว ****
# และเปลี่ยน key_path ให้ดึงมาจาก Environment Variable ถ้าใช้ Render
# key_path = os.environ.get("SERVICE_ACCOUNT_KEY_PATH")

if not os.path.exists(key_path):
    raise FileNotFoundError(f"Credential file not found at {key_path}")

credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1

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
def get_token(code, shop_id):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())

    payload = {
        "code": code,
        "shop_id": int(shop_id)
    }

    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}

    resp = requests.post(
        url,
        json=payload,
        headers=headers,
        params={
            "partner_id": SHOPEE_PARTNER_ID,
            "timestamp": timestamp,
            "sign": sign
        }
    )

    print("==== Shopee API Debug ====")
    print("Request URL:", resp.request.url)
    print("Request Headers:", resp.request.headers)
    print("Request Body:", resp.request.body)
    print("Status:", resp.status_code)
    print("Response:", resp.text)

    try:
        return resp.json()
    except Exception:
        return {"status": "error", "raw": resp.text}

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