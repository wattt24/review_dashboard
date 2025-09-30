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
from utils.config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET


def check_facebook_token(access_token: str) -> dict:
    """
    ตรวจสอบว่า token ของ Facebook เป็น long-lived หรือยัง
    และคืนค่ารายละเอียด เช่น expires_at, is_valid
    """
    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"  # app token
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    if "data" not in data:
        raise ValueError(f"❌ Invalid response from Facebook API: {data}")

    token_info = data["data"]

    expires_at = token_info.get("expires_at", 0)
    is_valid = token_info.get("is_valid", False)

    # แปลงเป็น human readable
    import datetime
    if expires_at:
        expires_str = datetime.datetime.fromtimestamp(expires_at).isoformat()
    else:
        expires_str = "ไม่ทราบ"

    print("=== Facebook Token Debug ===")
    print(f"✅ Valid: {is_valid}")
    print(f"📅 Expiry: {expires_str}")
    print(f"📌 Type: {token_info.get('type')}")
    print(f"👤 User/Page ID: {token_info.get('user_id', token_info.get('page_id'))}")
    print("============================")

    return token_info


# 🔹 ตัวอย่างการใช้งาน
if __name__ == "__main__":
    test_token = "EAAfvUL3Dgv8BPgxrvkEDtVdfZABl4R16AgCtE7l45a4J7vVrXTTbBBMUWYKZBLL2KZC1INAsTTg0WtCrNNgrZCs1G0i84vhN45HuUJjRX38zLFcpU1IDtsvnz9B1LHzb0hwh4979QfmJIbxo4ZBrdl8prPQrOKwrEqjHokFQvlrNiXUwPa9vV8hu8DByTlCKfi5NQac0RIBs4gzJt9oUyX5N1yxQ66e0Wf6PH"
    try:
        info = check_facebook_token(test_token)
    except Exception as e:
        print(f"Error: {e}")
