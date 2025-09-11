import re
import unicodedata
import hmac
import hashlib
import time
import requests
import os
from datetime import datetime
from utils.config import FACEBOOK_APP_SECRET,FACEBOOK_APP_ID
def sanitize_shopee_secret(secret_raw: str) -> str:
    """
    คืนค่าเป็น hex string ที่สะอาด (lowercase, ไม่มี whitespace/zero-width/BOM)
    ถ้าไม่ใช่ hex หรือความยาวไม่ถูกต้อง จะ raise ValueError
    """
    if not isinstance(secret_raw, str):
        raise ValueError("Secret ต้องเป็นสตริง")

    # 1) ตัดช่องว่างหัวท้าย + normalize unicode
    s = unicodedata.normalize("NFKC", secret_raw.strip())

    # 2) ลบ whitespace และตัวอักษรซ่อน
    remove_chars = [
        "\t", "\n", "\r", " ", "\u00A0",   # whitespace + NBSP
        "\u200B", "\u200C", "\u200D",      # zero-width
        "\uFEFF",                          # BOM
    ]
    trans = {ord(ch): None for ch in remove_chars}
    s = s.translate(trans).lower()

    # 3) ตรวจว่าเป็น hex
    if not re.fullmatch(r"[0-9a-f]+", s or ""):
        bad = [c for c in s if c not in "0123456789abcdef"]
        raise ValueError(f"❌ Secret ไม่ใช่ hex ถูกต้อง (มีอักษรแปลก: {bad[:10]})")

    # 4) ความยาวต้องเป็นจำนวนคู่
    if len(s) % 2 != 0:
        raise ValueError(f"❌ ความยาว hex ต้องเป็นจำนวนคู่ (ได้ {len(s)})")

    if len(s) not in (64, 128):
        print(f"⚠️ [คำเตือน] ความยาว hex = {len(s)} (ปกติ Shopee ใช้ 64 หรือ 128)")

    return s


def shopee_sign_example(partner_id: int, path: str, key_hex: str, ts=None) -> str:
    """สร้าง HMAC-SHA256 signature ตัวอย่าง"""
    if ts is None:
        ts = int(time.time())
    base_string = f"{partner_id}{path}{ts}"
    return hmac.new(bytes.fromhex(key_hex), base_string.encode("utf-8"), hashlib.sha256).hexdigest()


if __name__ == "__main__":
    # ---- วาง Partner Key ของคุณตรงนี้ ----
    secret_raw = """
    746161577650576364596f5657646c596b49705772546b4a52446a416b42
    """

    try:
        key_hex = sanitize_shopee_secret(secret_raw)
        key_bytes = bytes.fromhex(key_hex)

        print("✅ Partner Key ตรวจสอบแล้วใช้งานได้")
        print("- Hex length:", len(key_hex))
        print("- Byte length:", len(key_bytes))
        print("- ตัวอย่าง 8 ไบต์แรก:", key_bytes[:8].hex())

        # ทดสอบทำ signature
        partner_id = 123456  # <- เปลี่ยนเป็น Partner ID จริงของคุณ
        path = "/api/v2/shop/get_shop_info"
        signature = shopee_sign_example(partner_id, path, key_hex)
        print("- ตัวอย่าง signature:", signature)

    except ValueError as e:
        print(str(e))


FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET") 

def check_token_expiry(access_token: str):
    """
    ตรวจสอบ Access Token ของ Facebook ว่าเป็น Long-Lived หรือ Short-Lived
    และบอกวันหมดอายุ
    """
    # App Access Token (APP_ID|APP_SECRET)
    app_access_token = f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"

    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": app_access_token
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "data" not in data:
        return {"error": data}

    token_info = data["data"]
    result = {
        "app_id": token_info.get("app_id"),
        "type": token_info.get("type"),
        "application": token_info.get("application"),
        "is_valid": token_info.get("is_valid"),
        "scopes": token_info.get("scopes"),
    }

    # วันหมดอายุ
    expires_at = token_info.get("expires_at")
    if expires_at:
        expiry_date = datetime.fromtimestamp(expires_at)
        result["expires_at"] = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # เช็คว่า Long-Lived หรือ Short-Lived
        days_left = (expiry_date - datetime.now()).days
        if days_left > 7:  # ถ้าเกิน 7 วัน ถือว่า Long-Lived
            result["token_type"] = "Long-Lived"
        else:
            result["token_type"] = "Short-Lived"
    else:
        result["expires_at"] = "ไม่พบวันหมดอายุ"
        result["token_type"] = "Unknown"

    return result
