# utils/lazada_auth.py
import uuid
import urllib.parse
import os
import time, hmac, hashlib
import requests
import json
from datetime import datetime
from datetime import datetime, timedelta
from utils.token_manager import get_gspread_client , save_token , get_latest_token# ถ้าจะเก็บ mapping ลง Google Sheet
from utils.config import (LAZADA_APP_ID, LAZADA_REDIRECT_URI, GOOGLE_SHEET_ID, LAZADA_APP_SECRET)
LAZADA_ACCESS_TOKEN = None
from lazop.base import LazopClient, LazopRequest
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
#ใช้ได้
def lazada_exchange_token(code: str):
    """
    แลก authorization code จาก Lazada เพื่อขอ access_token และ refresh_token
    พร้อม debug log ครบทุกขั้นตอน
    """
    try:
        path = "/auth/token/create"
        url = f"https://auth.lazada.com/rest{path}"

        # ✅ ใส่เฉพาะพารามิเตอร์ที่ Lazada ต้องการ
        params = {
            "app_key": LAZADA_APP_ID,
            "code": code,
            "sign_method": "sha256",
            "timestamp": str(int(time.time() * 1000))
        }

        # ✅ เรียงตามชื่อ A-Z
        sorted_items = sorted(params.items())
        concatenated = ''.join([f"{k}{v}" for k, v in sorted_items])

        # ✅ สร้าง base string และเซ็นด้วย HMAC-SHA256
        base_string = path + concatenated
        sign_bytes = hmac.new(
            LAZADA_APP_SECRET.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().upper()

        params["sign"] = sign_bytes

        # 🧩 DEBUG LOG DETAIL
        print("\n==================== LAZADA TOKEN DEBUG ====================")
        print("⏰ Local UTC Time:", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        print("🌍 Endpoint URL:", url)
        print("🧾 Raw Parameters (Before sort):", json.dumps(params, indent=2))
        print("🔡 Sorted & Concatenated Params:", concatenated)
        print("🧮 Base String to Sign:", base_string)
        print("🔐 App Secret (hidden):", LAZADA_APP_SECRET[:4] + "..." + LAZADA_APP_SECRET[-4:])
        print("✅ Generated Signature:", sign_bytes)
        print("📤 Sending POST request to Lazada...")
        print("============================================================\n")

        # ✅ ส่ง request (ใช้ POST)
        response = requests.post(url, data=params, timeout=10)

        print("📬 HTTP Status Code:", response.status_code)

        try:
            data = response.json()
        except Exception:
            print("⚠️ Failed to decode JSON, raw text returned.")
            data = {"raw_text": response.text}

        print("🔹 Lazada token response:", json.dumps(data, indent=2))
        print("============================================================\n")

        return data

    except Exception as e:
        print("❌ Error exchanging token:", str(e))
        return {"error": str(e)}
# ตัวกลาง sdk ในการเรียก Lazada API
def call_lazada_api(endpoint, method="GET", params=None):
    """
    ฟังก์ชันกลางสำหรับเรียก Lazada API ผ่าน SDK
    """
    try:
        client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
        request = LazopRequest(endpoint, method)

        if params:
            for k, v in params.items():
                request.add_api_param(k, str(v))

        response = client.execute(request, LAZADA_ACCESS_TOKEN)

        # ✅ บาง SDK จะคืน dict, บางตัวคืน string
        if isinstance(response.body, (str, bytes)):
            data = json.loads(response.body)
        else:
            data = response.body

        return data

    except Exception as e:
        print(f"❌ Error calling Lazada API: {str(e)}")
        return {"error": str(e)}


# ====== ฟังก์ชันย่อยเฉพาะ ======

def lazada_get_products(offset=0, limit=10):
    """
    ดึงรายการสินค้าในร้าน
    """
    return call_lazada_api(
        endpoint="/products/get",
        method="GET",
        params={
            "offset": offset,
            "limit": limit
        }
    )

# ใช้ได้
def lazada_refresh_access_token(account_id):
    """
    🔄 รีเฟรช Lazada Access Token ผ่าน Lazop SDK และบันทึกลง Google Sheet
    """
    # ดึง refresh_token ล่าสุดจาก Google Sheet
    token_data = get_latest_token(platform="lazada", account_id=seller_id)
    if not token_data or not token_data.get("refresh_token"):
        print(f"❌ ไม่พบ refresh_token สำหรับ account_id {account_id}")
        return None

    refresh_token = token_data["refresh_token"]

    print("\n================ Lazada API Debug Info ================")
    print(f"🔹 API Name: /auth/token/refresh")
    print(f"🔹 Refresh Token: {refresh_token}")
    print(f"🔹 Account ID: {seller_id}")
    print("=======================================================\n")

    # เรียกผ่าน SDK ด้วยฟังก์ชันกลาง
    response = call_lazada_api(
        endpoint="/auth/token/refresh",
        method="POST",
        params={"refresh_token": refresh_token}
    )

    # ตรวจสอบผลลัพธ์
    if not response:
        print("❌ ไม่พบข้อมูล response จาก Lazada SDK")
        return None

    data = response.get("data") or response  # บาง SDK ห่ออยู่ใน "data"

    access_token = data.get("access_token")
    new_refresh = data.get("refresh_token")
    expires_in = data.get("expires_in")

    if access_token and new_refresh:
        
        seller_id = data.get("account")  # Lazada seller ID
        save_token(
            platform="lazada",
            account_id=seller_id,
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=expires_in
        )
        expire_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        print(f"✅ Lazada token refreshed successfully (expires at {expire_time})")
    else:
        print("❌ Failed to refresh Lazada access token:", response)

    return response


