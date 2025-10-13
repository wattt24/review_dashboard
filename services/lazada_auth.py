# utils/lazada_auth.py
import uuid
import urllib.parse
import os
import time, hmac, hashlib
import requests
from datetime import datetime
from datetime import datetime, timedelta
from utils.token_manager import get_gspread_client , save_token , get_latest_token# ถ้าจะเก็บ mapping ลง Google Sheet
from utils.config import (LAZADA_APP_ID, LAZADA_REDIRECT_URI, GOOGLE_SHEET_ID, LAZADA_APP_SECRET)

def lazada_generate_state(store_id):
    # state ควรเป็น unique + ยากเดา
    return f"{store_id}-{uuid.uuid4().hex}"
# Authorization
# สร้าง state สําหรับ Lazada
def lookup_store_from_state(state: str):
    """อ่าน store_id จาก state ใน Google Sheet"""
    client = get_gspread_client()
    ss = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        ws = ss.worksheet("state_mapping")
    except Exception:
        return None
    records = ws.get_all_records()
    for r in records:
        if r.get("state") == state:
            return r.get("store_id")
    return None


def lazada_save_state_mapping_to_sheet(state, store_id):
    """เก็บ mapping state → store_id ลง Google Sheet"""
    client = get_gspread_client()
    ss = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        ws = ss.worksheet("state_mapping")
    except Exception:
        ws = ss.add_worksheet("state_mapping", rows=1000, cols=10)
        ws.append_row(["state", "store_id", "created_at"])
    ws.append_row([state, store_id, datetime.utcnow().isoformat()])

def lazada_get_auth_url_for_store(store_id: str) -> str:
    """
    ใช้สำหรับ generate ลิงก์ Lazada Authorization สำหรับร้านค้า
    """
    state = lazada_generate_state(store_id)
    lazada_save_state_mapping_to_sheet(state, store_id)
    return build_lazada_auth_url(state)
def build_lazada_auth_url(state):
    base = "https://auth.lazada.com/oauth/authorize"
    params = {
        "response_type": "code",
        "client_id": LAZADA_APP_ID,
        "redirect_uri": LAZADA_REDIRECT_URI,  # ปล่อยเป็น raw
        "state": state,
        "force_auth": "true",
        "country": "th",
    }
    qs = urllib.parse.urlencode(params)  # urlencode จะ encode ให้เอง
    return f"{base}?{qs}"
# สร้าง sign เพื่อ  generate token
def lazada_generate_sign(params: dict, app_secret: str) -> str:
    # 1. เรียง key ตามตัวอักษร
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    # 2. ต่อ string เป็น k1v1k2v2...
    base_string = "".join(f"{k}{v}" for k, v in sorted_params)
    # 3. HMAC-SHA256
    sign = hmac.new(
        app_secret.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    print("Base string for HMAC:", base_string)
    return sign
def lazada_generate_sign(params, app_secret):
    # ต้องเรียง key ตามตัวอักษร
    sorted_params = sorted(params.items())
    concat_str = ""
    for k, v in sorted_params:
        concat_str += f"{k}{v}"
    
    # prepend ด้วย /rest/auth/token/create
    concat_str = "/rest/auth/token/create" + concat_str
    
    sign = hmac.new(
        app_secret.encode("utf-8"),
        concat_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()
    return sign
def lazada_exchange_token(code: str):

    china_time = datetime.utcnow() + timedelta(hours=8)
    timestamp = int(china_time.timestamp() * 1000)
    grant_type = "authorization_code"

    # สร้าง base string สำหรับ sign
    base_str = (
        f"app_key{LAZADA_APP_ID}"
        f"code{code}"
        f"grant_type{grant_type}"
        f"redirect_uri{LAZADA_REDIRECT_URI}"
        f"timestamp{timestamp}"
    )

    # สร้าง signature ด้วย SHA256
    sign = hmac.new(
        LAZADA_APP_SECRET.encode("utf-8"),
        base_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest().upper()

    payload = {
        "app_key": LAZADA_APP_ID,
        "code": code,
        "grant_type": grant_type,
        "redirect_uri": LAZADA_REDIRECT_URI,
        "timestamp": timestamp,
        "sign_method": "sha256",  # ✅ เพิ่มบรรทัดนี้
        "sign": sign
    }

    print("🔁 Requesting access token from Lazada...")
    print("Payload for token request:", payload)

    url = "https://auth.lazada.com/rest/auth/token/create"
    response = requests.post(url, data=payload)
    print("status_code:", response.status_code)
    print("resp.text:", response.text)

    return response.json()
# def lazada_exchange_token(code: str):
#     import requests

#     timestamp = int(time.time())
#     base_str = f"app_key{LAZADA_APP_ID}app_secret{LAZADA_APP_SECRET}code{code}grant_typeauthorization_coderedirect_uri{LAZADA_REDIRECT_URI}timestamp{timestamp}"
#     sign = hmac.new(
#         LAZADA_APP_SECRET.encode("utf-8"),
#         base_str.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest().upper()

#     payload = {
#         "app_key": LAZADA_APP_ID,
#         "app_secret": LAZADA_APP_SECRET,
#         "code": code,
#         "grant_type": "authorization_code",
#         "redirect_uri": LAZADA_REDIRECT_URI,
#         "timestamp": timestamp,
#         "sign": sign
#     }

#     url = "https://auth.lazada.com/rest/auth/token/create"
#     response = requests.post(url, data=payload)
#     print("Payload for token request:", payload)
#     return response.json()
# def lazada_exchange_token(code: str):
#     token_url = "https://auth.lazada.com/rest/auth/token/create"
#     payload = {
#         "code": code,
#         "app_key": LAZADA_CLIENT_ID,
#         "app_secret": LAZADA_CLIENT_SECRET,
#         "grant_type": "authorization_code",
#         "redirect_uri": LAZADA_REDIRECT_URI
#     }

#     payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

#     # Lazada ต้องการ form-urlencoded
#     resp = requests.post(
#     token_url,
#     data=payload,
#     headers={"Content-Type": "application/x-www-form-urlencoded"}
#     )
#     print("Payload for token request:", payload)
#     print("status_code:", resp.status_code)
#     print("resp.text:", resp.text)

#     sorted_params = sorted(payload.items(), key=lambda x: x[0])
#     base_string = "".join(f"{k}{v}" for k, v in sorted_params)
#     print("Base string for HMAC:", base_string)

#     return resp.json()
# def lazada_exchange_token(code):
#     url = "https://auth.lazada.com/rest/auth/token/create"
#     payload = {
#         "code": code,
#         "app_key": LAZADA_CLIENT_ID,
#         "app_secret": LAZADA_CLIENT_SECRET,
#         "grant_type": "authorization_code",
#         "redirect_uri": LAZADA_REDIRECT_URI
#     }

#     response = requests.post(url, data=payload)
#     print("🔹 Lazada token response:", response.json())
#     return response.json()

# refresh token
def lazada_refresh_token(refresh_token: str, store_id: str):
    """ใช้ refresh_token เพื่อขอ access_token ใหม่"""
    token_url = "https://auth.lazada.com/rest/auth/token/create"
    timestamp = int(time.time() * 1000)

    payload = {
        "app_key": LAZADA_APP_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "timestamp": timestamp,
        "sign_method": "sha256",
    }

    payload["sign"] = lazada_generate_sign(payload, LAZADA_APP_SECRET)

    resp = requests.post(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    data = resp.json()

    print("DEBUG Refresh token response:", data)

    if "access_token" not in data:
        raise Exception(f"Lazada refresh token failed: {data}")

    save_token(
        "lazada",
        store_id,
        data["access_token"],
        data.get("refresh_token", refresh_token),
        data.get("expires_in", 0),
        data.get("refresh_expires_in", 0)
    )
    return data

