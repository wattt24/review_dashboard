PARTNER_ID = 2012650
PARTNER_KEY = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
SHOP_ID = 57360480
REFRESH_TOKEN = "704a5355526b4c57464762524c734b4d"
import time, hmac, hashlib, requests #path = "/api/v2/auth/access_token/get"
import datetime
# from utils.config import PARTNER_ID, PARTNER_KEY, SHOP_ID,REFRESH_TOKEN

from utils.token_manager import save_token
import time
import hmac
import hashlib
import requests
import datetime
# from utils.config import PARTNER_ID, PARTNER_KEY, SHOP_ID, REFRESH_TOKEN

# def get_shopee_access_token():
#     """
#     ขอ Access Token ใหม่จาก Shopee Partner API และบันทึกลง Google Sheet
#     """
#     timestamp = int(time.time())
#     path = "/api/v2/auth/access_token/get"
#     base_string = f"{PARTNER_ID}{path}{timestamp}"
#     sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

#     url = f"https://partner.shopeemobile.com{path}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}"
#     body = {
#         "partner_id": PARTNER_ID,
#         "shop_id": SHOP_ID,
#         "refresh_token": REFRESH_TOKEN
#     }

#     # ===== DEBUG LOG =====
#     request_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone(datetime.timedelta(hours=7)))
#     print("\n================ Shopee API Debug Info ================")
#     print(f"🔹 API Name: {path}")
#     print(f"🔹 Full Request URL: {url}")
#     print(f"🔹 Request Time (TH timezone): {request_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
#     print(f"🔹 Partner ID: {PARTNER_ID}")
#     print(f"🔹 Shop ID: {SHOP_ID}")
#     print(f"🔹 Request Parameters: {body}")
#     print("=======================================================\n")

#     # ===== ส่ง Request =====
#     try:
#         response = requests.post(url, json=body, timeout=15)
#         data = response.json()
#     except Exception as e:
#         print("❌ Request failed:", e)
#         return None

#     # ===== LOG ผลลัพธ์ =====
#     print("🟢 Response:")
#     print(data)
#     if "request_id" in data:
#         print(f"🔸 Request ID: {data['request_id']}")
#     print("\n=======================================================\n")

#     # ===== บันทึกลง Google Sheet =====
#     if data.get("access_token") and data.get("refresh_token"):
#         expires_in = data.get("expires_in")  # คำนวณเวลาหมดอายุ Access Token
#         save_token(
#             platform="Shopee",
#             account_id=SHOP_ID,
#             access_token=data["access_token"],
#             refresh_token=data["refresh_token"],
#             expires_in=expires_in
#         )
#         print(f"✅ Shopee token saved to Google Sheet for shop {SHOP_ID}")

#     return data



timestamp = int(time.time())
path = "/api/v2/auth/access_token/get"
base_string = f"{PARTNER_ID}{path}{timestamp}"
sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

url = f"https://partner.shopeemobile.com{path}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}"

body = {
    "partner_id": PARTNER_ID,
    "shop_id": SHOP_ID,
    "refresh_token": REFRESH_TOKEN
}

# ====== DEBUG PRINTS ======
# Local timezone (+07:00 for Thailand)
request_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone(datetime.timedelta(hours=7)))

print("\n================ Shopee API Debug Info ================")
print(f"🔹 API Name: {path}")
print(f"🔹 Full Request URL: {url}")
print(f"🔹 Request Time (TH timezone): {request_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"🔹 Partner ID: {PARTNER_ID}")
print(f"🔹 Shop ID: {SHOP_ID}")
print(f"🔹 Request Parameters: {body}")
print("=======================================================\n")

# ====== SEND REQUEST ======
try:
    response = requests.post(url, json=body)
    data = response.json()
except Exception as e:
    print("❌ Request failed:", e)
    data = None

# ====== RESPONSE LOG ======
print("🟢 Response:")
# if data:
#     print(data)
#     if "request_id" in data:
#         print(f"🔸 Request ID: {data['request_id']}")
# else:
#     print("❌ No response data returned.")

# if data.get("access_token") and data.get("refresh_token"):
#         expires_in = data.get("expires_in")  # คำนวณเวลาหมดอายุ Access Token
#         save_token(
#             platform="Shopee",
#             account_id=SHOP_ID,
#             access_token=data["access_token"],
#             refresh_token=data["refresh_token"],
#             expires_in=expires_in
#         )
#         print(f"✅ Shopee token saved to Google Sheet for shop {SHOP_ID}")
# print("\n=======================================================\n")
if data.get("access_token") and data.get("refresh_token"):
    expires_in = data.get("expires_in")
    save_token(
        platform="Shopee",
        account_id=SHOP_ID,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=expires_in,
        timestamp=timestamp  # ✅ เพิ่มบันทึก timestamp ที่ใช้ใน request
    )
    print(f"✅ Shopee token saved to Google Sheet for shop {SHOP_ID}")
