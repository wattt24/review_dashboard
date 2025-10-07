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
import requests

ACCESS_TOKEN = "EAAfvUL3Dgv8BPmmzJxQhlA096ZC2UK0rXZBXDG8tJySWVZBRLLopdSPHK1ZCklWbxI8ZBxY99rMI4DU72YafUA1ykCE49tKFl8V7sbk8D6f0ZBKUg8nHDvCCp6CaSSvVFZCCVKtyyEMGvMBZBZCRmSZAR9RyrnAL5I5nHuUyc6eqm2JqZBY2yvpKBDbQLNAj2AY23IrSpsovNCZABpZAqEIWKbCGargqUN2h2fgbAnCND"
PAGE_ID = "110736563133006"  # Fujika Thailand

url = f"https://graph.facebook.com/v19.0/{PAGE_ID}?fields=name,fan_count"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

r = requests.get(url, headers=headers)
print(r.json())
