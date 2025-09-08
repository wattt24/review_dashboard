# services/test_auth.py
# services/test_auth.py
import os
import streamlit as st
import time
import hmac
import hashlib
import requests
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_REDIRECT_URI
)

# Shopee Base URL
SANDBOX = True
BASE_URL = "https://partner.test-stable.shopeemobile.com" if SANDBOX else "https://partner.shopeemobile.com"

# ---------------- Google Sheets ----------------
def get_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds_dict = st.secrets["SERVICE_ACCOUNT_JSON"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["GOOGLE_SHEET_ID"]).sheet1
    return sheet

# ---------------- Signature Utils ----------------
def generate_sign(base_string: str) -> str:
    """Generic HMAC-SHA256 signature generator"""
    return hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def generate_auth_sign(path, timestamp):
    """Sign for auth step (/shop/auth_partner)"""
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    return generate_sign(base_string)

def generate_token_sign(path, timestamp):
    """Sign for /auth/token/get"""
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}"
    return generate_sign(base_string)

def generate_refresh_sign(path, timestamp, refresh_token_value, shop_id):
    """Sign for /auth/access_token/get"""
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{refresh_token_value}{int(shop_id)}"
    return generate_sign(base_string)

def generate_api_sign(path, timestamp, access_token, shop_id):
    """Sign for general shop APIs"""
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{int(shop_id)}"
    return generate_sign(base_string)

# ---------------- OAuth Flow ----------------
def get_authorization_url():
    """Generate shop authorization URL"""
    path = "/api/v2/shop/auth_partner"
    timestamp = int(time.time())
    sign = generate_auth_sign(path, timestamp)

    url = (
        f"{BASE_URL}{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
        f"&redirect={SHOPEE_REDIRECT_URI}"
    )
    return url

def get_token(code, shop_id):
    """Exchange auth code for access & refresh tokens"""
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())
    sign = generate_token_sign(path, timestamp)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }

    resp = requests.post(url, json=payload)
    print("==== DEBUG get_token ====")
    print("base_string:", f"{SHOPEE_PARTNER_ID}{path}{timestamp}")
    print("sign:", sign)
    print("url:", url)
    print("payload:", payload)
    print("response:", resp.text)
    return resp.json()

def refresh_token(refresh_token_value, shop_id):
    """Refresh access token"""
    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = generate_refresh_sign(path, timestamp, refresh_token_value, shop_id)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "refresh_token": refresh_token_value,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }

    resp = requests.post(url, json=payload)
    print("==== DEBUG refresh_token ====")
    print("payload:", payload)
    print("response:", resp.text)
    return resp.json()

# ---------------- Generic API Call ----------------
def call_shopee_api(path, shop_id, access_token, method="GET", payload=None):
    """Call any Shopee shop API"""
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


from datetime import datetime, timezone

def get_token(code, shop_id):
    path = "/api/v2/auth/token/get"
    # ใช้ UTC timestamp แทน
    timestamp = int(datetime.now(timezone.utc).timestamp())
    sign = generate_token_sign(path, timestamp)

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"
    payload = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": int(SHOPEE_PARTNER_ID)
    }

    resp = requests.post(url, json=payload)
    print("==== DEBUG get_token ====")
    print("base_string:", f"{SHOPEE_PARTNER_ID}{path}{timestamp}")
    print("sign:", sign)
    print("url:", url)
    print("payload:", payload)
    print("response:", resp.text)
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

def save_token(platform, account_id, access_token, refresh_token_value, expires_in, refresh_expires_in):
    sheet = get_sheet()

    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat() if refresh_expires_in else ""

    try:
        cell = sheet.find(str(account_id))
        row = cell.row
        sheet.update(
            f"A{row}:F{row}",
            [[platform, account_id, access_token, refresh_token_value, expired_at, refresh_expired_at]]
        )
        sheet.update(f"G{row}", datetime.now().isoformat())
    except gspread.exceptions.CellNotFound:
        sheet.append_row([
            platform, account_id, access_token, refresh_token_value,
            expired_at, refresh_expired_at, datetime.now().isoformat()
        ])

def get_latest_token(platform, account_id):
    sheet = get_sheet()
    records = sheet.get_all_records()
    for record in records:
        if str(record["platform"]) == str(platform) and str(record["account_id"]) == str(account_id):
            return {
                "access_token": record["access_token"],
                "refresh_token": record.get("refresh_token", ""),
                "expired_at": record.get("expired_at", ""),
                "refresh_expired_at": record.get("refresh_expired_at", "")
            }
    return None

def get_valid_access_token(platform, account_id, refresh_func=None):
    token = get_latest_token(platform, account_id)
    if not token:
        return None

    if token["expired_at"]:
        expired_at = datetime.fromisoformat(token["expired_at"])
    else:
        return token["access_token"]  # ไม่มีวันหมดอายุ เช่น Facebook long-lived

    if datetime.now() >= expired_at:
        if refresh_func and token["refresh_token"] and token["refresh_expired_at"]:
            refresh_expired_at = datetime.fromisoformat(token["refresh_expired_at"])
            if datetime.now() < refresh_expired_at:
                new_tokens = refresh_func(token["refresh_token"], account_id)
                if "access_token" in new_tokens:
                    save_token(
                        platform, account_id,
                        new_tokens["access_token"],
                        new_tokens.get("refresh_token", ""),
                        new_tokens.get("expires_in"),
                        new_tokens.get("refresh_expires_in")
                    )
                    return new_tokens["access_token"]
        return None
    else:
        return token["access_token"]
