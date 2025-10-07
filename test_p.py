# import time, hmac, hashlib, requests

# BASE_URL = "https://partner.shopeemobile.com"
# PARTNER_ID = "2012650"
# PARTNER_KEY = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
# SHOP_ID = "57360480"
# ACCESS_TOKEN = "4f4d4c4e6944554d7945727a774e6452"



# def sign_request(path, timestamp, access_token, shop_id):
#     base_string = f"{PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
#     return hmac.new(
#         PARTNER_KEY.encode("utf-8"),
#         base_string.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()

# def get_shop_performance():
#     path = "/api/v2/shop/get_shop_performance"
#     timestamp = int(time.time())
#     sign = sign_request(path, timestamp, ACCESS_TOKEN, SHOP_ID)

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": ACCESS_TOKEN,
#         "shop_id": SHOP_ID
#     }

#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()

# def get_shop_summary():
#     path = "/api/v2/shop/get_shop_summary"
#     timestamp = int(time.time())
#     sign = sign_request(path, timestamp, ACCESS_TOKEN, SHOP_ID)

#     url = f"{BASE_URL}{path}"
#     params = {
#         "partner_id": PARTNER_ID,
#         "timestamp": timestamp,
#         "sign": sign,
#         "access_token": ACCESS_TOKEN,
#         "shop_id": SHOP_ID
#     }

#     resp = requests.get(url, params=params, timeout=15)
#     return resp.json()


# # 🔄 เรียกใช้งาน
# print("== Shop Performance ==")
# print(get_shop_performance())

# print("\n== Shop Summary ==")
# print(get_shop_summary())
import hmac
import hashlib
import base64
import json

channel_secret = '516d493d9689e0c8c11bec8256e92cc6'

body = {
  "events": [
    {
      "type": "message",
      "replyToken": "dummy_token",
      "source": {
        "userId": "U1234567890abcdef",
        "type": "user"
      },
      "timestamp": 1691234567890,
      "mode": "active",
      "message": {
        "type": "text",
        "id": "1234567890",
        "text": "ทดสอบข้อความ"
      }
    }
  ]
}

# ต้องใช้ json.dumps แบบไม่เว้นวรรค
body_str = json.dumps(body, separators=(',', ':'), ensure_ascii=False)
body_bytes = body_str.encode('utf-8')

hash = hmac.new(channel_secret.encode('utf-8'), body_bytes, hashlib.sha256).digest()
signature = base64.b64encode(hash).decode()

print("🔐 X-Line-Signature:", signature)
