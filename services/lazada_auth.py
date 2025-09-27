# utils/lazada_auth.py
import uuid
import urllib.parse
import os
import time, hmac, hashlib
import requests
from datetime import datetime
from utils.token_manager import get_gspread_client  # ถ้าจะเก็บ mapping ลง Google Sheet
from utils.config import (LAZADA_CLIENT_ID, LAZADA_REDIRECT_URI, GOOGLE_SHEET_ID, LAZADA_CLIENT_SECRET)


# สร้าง state สําหรับ Lazada
def lazada_generate_state(store_id):
    # state ควรเป็น unique + ยากเดา
    return f"{store_id}-{uuid.uuid4().hex}"

def lazada_save_state_mapping_to_sheet(state, store_id):
    client = get_gspread_client()
    ss = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        ws = ss.worksheet("state_mapping")
    except Exception:
        ws = ss.add_worksheet("state_mapping", rows=1000, cols=10)
        ws.append_row(["state","store_id","created_at"])
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
        "force_auth": "true",
        "redirect_uri": LAZADA_REDIRECT_URI,
        "client_id": LAZADA_CLIENT_ID,
        "state": state
    }
    qs = urllib.parse.urlencode(params)

    return f"{base}?{qs}"
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
    return sign


def lazada_exchange_token(code: str):
    token_url = "https://auth.lazada.com/rest/auth/token"
    timestamp = int(time.time() * 1000)

    payload = {
    "app_key": LAZADA_CLIENT_ID,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": LAZADA_REDIRECT_URI,  # ต้องตรงกับ Developer Console
    "timestamp": int(time.time() * 1000),
    "sign_method": "sha256",
    }

    payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

    # Lazada ต้องการ form-urlencoded
    resp = requests.post(
        "https://auth.lazada.com/rest/auth/token",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
)

    print("Payload for token request:", payload)
    sorted_params = sorted(payload.items(), key=lambda x: x[0])
    base_string = "".join(f"{k}{v}" for k, v in sorted_params)
    print("Base string for HMAC:", base_string)

    return resp.json()
