# services/shopee_auth.py
import os
import time
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.config import (
    SHOPEE_PARTNER_ID, 
    SHOPEE_PARTNER_SECRET, 
    SHOPEE_REDIRECT_URI
)
#key_path = "data/service_account.json"
key_path = "/etc/secrets/service_account.json"
#--------
# ใช้ path แบบ Windows-friendly (อยู่ในโฟลเดอร์ data)
# scope สำหรับ Google API
# scope = ["https://spreadsheets.google.com/feeds",
#          "https://www.googleapis.com/auth/drive"]
# key_path = os.path.join("data", "service_account.json")
credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(credentials)
sheet_id = os.environ.get("GOOGLE_SHEET_ID")
sheet = client.open_by_key(sheet_id).sheet1
# ใส่ path ตามที่ Render กำหนด

scope = [
     "https://spreadsheets.google.com/feeds",
     "https://www.googleapis.com/auth/drive"
     ]

# ตรวจสอบว่ามีไฟล์ดังกล่าวจริงก่อนใช้งาน
if not os.path.exists(key_path):
    raise FileNotFoundError(f"Credential file not found at {key_path}")

credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1
#--------
# โหลด credentials render

# ===================== Shopee OAuth & API =====================
def generate_sign(path, partner_id, timestamp, redirect_url, partner_secret):
    base_string = f"{partner_id}{path}{timestamp}{redirect_url}"
    return hmac.new(
        partner_secret.encode(),
        base_string.encode(),
        hashlib.sha256
    ).hexdigest()

def get_authorization_url():
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = generate_sign(path, SHOPEE_PARTNER_ID, timestamp, SHOPEE_REDIRECT_URI, SHOPEE_PARTNER_SECRET)

    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )
    return url

def generate_signature(path, timestamp, access_token=None, shop_id=None):
    base_str = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    if access_token and shop_id:
        base_str = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode(),
        base_str.encode(),
        hashlib.sha256
    ).hexdigest()

def get_token(code, shop_id):
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "code": code,
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id
    }

    r = requests.post(url, json=payload)
    return r.json()

def refresh_token(refresh_token_value, shop_id):
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token_value,
        "partner_id": SHOPEE_PARTNER_ID,
        "shop_id": shop_id
    }

    r = requests.post(url, json=payload)
    return r.json()

def call_shopee_api(path, access_token, shop_id, params=None):
    timestamp = int(time.time())
    sign = generate_signature(path, timestamp, access_token, shop_id)

    url = f"https://partner.shopeemobile.com{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&access_token={access_token}&shop_id={shop_id}&sign={sign}"
    r = requests.get(url, params=params)
    return r.json()

# ===================== Google Sheets token management =====================
def save_token(shop_id, access_token, refresh_token_value, expires_in, refresh_expires_in):
    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat()

    # หา row ของ shop_id
    try:
        cell = sheet.find(str(shop_id))
        row = cell.row
        sheet.update(f"B{row}:E{row}", [[access_token, refresh_token_value, expired_at, refresh_expired_at]])
        sheet.update(f"F{row}", datetime.now().isoformat())
    except gspread.exceptions.CellNotFound:
        # ถ้าไม่มี shop_id ใหม่ → append
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

# ===================== Auto refresh token =====================
def get_valid_access_token(shop_id):
    token = get_latest_token(shop_id)
    if not token:
        return None

    expired_at = datetime.fromisoformat(token["expired_at"])
    refresh_expired_at = datetime.fromisoformat(token["refresh_expired_at"])

    # ถ้า access_token หมดอายุ → refresh
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
        return None  # ทั้ง access & refresh หมดอายุ
