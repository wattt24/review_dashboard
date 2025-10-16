# ใช้ได้
import os
os.environ["GOOGLE_SHEET_ID"] = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"

import time
import hmac
import hashlib
import requests
import datetime
from utils.token_manager import save_token, get_latest_token

def shopee_refresh_access_token(partner_id, partner_key, shop_id):
    """
    ขอ Access Token ใหม่จาก Shopee Partner API และบันทึกลง Google Sheet
    ดึงค่า refresh_token ล่าสุดจาก Google Sheet
    """
    # ====== ดึง refresh_token ล่าสุด ======
    token_data = get_latest_token(platform="shopee", account_id=shop_id)
    if not token_data or not token_data.get("refresh_token"):
        print(f"❌ ไม่พบ refresh_token สำหรับ shop_id {shop_id} ใน Google Sheet")
        return None

    refresh_token = token_data["refresh_token"]

    timestamp = int(time.time())
    path = "/api/v2/auth/access_token/get"
    base_string = f"{partner_id}{path}{timestamp}"
    sign = hmac.new(partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    url = f"https://partner.shopeemobile.com{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}"

    body = {
        "partner_id": partner_id,
        "shop_id": shop_id,
        "refresh_token": refresh_token
    }

    # ====== DEBUG PRINTS ======
    request_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone(datetime.timedelta(hours=7)))
    print("\n================ Shopee API Debug Info ================")
    print(f"🔹 API Name: {path}")
    print(f"🔹 Full Request URL: {url}")
    print(f"🔹 Request Time (TH timezone): {request_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🔹 Partner ID: {partner_id}")
    print(f"🔹 Shop ID: {shop_id}")
    print(f"🔹 Request Parameters: {body}")
    print("=======================================================\n")

    # ====== SEND REQUEST ======
    try:
        response = requests.post(url, json=body)
        data = response.json()
    except Exception as e:
        print("❌ Request failed:", e)
        return None

    # ====== RESPONSE LOG ======
    if data.get("access_token") and data.get("refresh_token"):
        expires_in = data.get("expires_in")
        save_token(
            platform="shopee",
            account_id=shop_id,
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=expires_in
        )
        print(f"✅ Shopee token saved to Google Sheet for shop {shop_id}")
        # ====== PRINT REQUEST ID ======
        if "request_id" in data:
            print(f"🆔 request_id: {data['request_id']}")
    else:
        print("❌ Failed to refresh Shopee access token:", data)

    return data

# ====== เรียกใช้งาน ======
SHOPEE_PARTNER_ID = 2012650
SHOPEE_PARTNER_KEY = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
SHOPEE_SHOP_ID = 57360480

shopee_refresh_access_token(
    partner_id=SHOPEE_PARTNER_ID,
    partner_key=SHOPEE_PARTNER_KEY,
    shop_id=SHOPEE_SHOP_ID
)
