#test
# from database.all_database import get_connection
# import pandas as pd

# conn = get_connection()
# df = pd.read_sql("SELECT * FROM reviews_history LIMIT 10", conn)
# conn.close()
# print(df.head())
# import time, hmac, hashlib, requests, json

# partner_id = "2012650"
# partner_secret = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
# shop_id = 57360480
# refresh_token = "624e4350715642794c41796a50766a49"  # ต้องเป็นตัวล่าสุด

# path = "/api/v2/auth/access_token/get"
# timestamp = int(time.time())

# # generate sign
# base_string = f"{partner_id}{path}{timestamp}"
# sign = hmac.new(
#     partner_secret.encode("utf-8"),
#     base_string.encode("utf-8"),
#     hashlib.sha256
# ).hexdigest()

# url = f"https://partner.shopeemobile.com{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}"

# body = {
#     "partner_id": int(partner_id),
#     "shop_id": shop_id,
#     "refresh_token": refresh_token
# }

# headers = {"Content-Type": "application/json"}

# resp = requests.post(url, headers=headers, data=json.dumps(body))

# print("✅ URL:", url)
# print("✅ Body:", body)
# print("📥 Response:", resp.json())
import time, hmac, hashlib, requests, json, os
from utils.token_manager import get_latest_token
# ===================== CONFIG =====================
PARTNER_ID = "2012650"
PARTNER_SECRET = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
SHOP_ID = 57360480
TOKEN_FILE = "shopee_token.json"  # เก็บ access + refresh token

# ===================== FUNCTION =====================
def generate_sign(path, timestamp):
    base_string = f"{PARTNER_ID}{path}{timestamp}"
    return hmac.new(
        PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def save_token(access_token, refresh_token, expire_in):
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expire_time": int(time.time()) + expire_in - 60  # ลด 60 วินาทีเผื่อเวลา
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Token saved to", TOKEN_FILE)

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def refresh_token_if_needed():
    token_data = load_token()
    now = int(time.time())

    # ถ้าไม่มี token หรือ access_token หมดอายุ
    if not token_data or now >= token_data.get("expire_time", 0):
        print("⏳ Refreshing Shopee token...")
        token_data = refresh_token(token_data["refresh_token"] if token_data else None)
    else:
        print("🟢 Access token ยัง valid")

    return token_data

def refresh_token(refresh_token_value):
    if not refresh_token_value:
        raise ValueError("❌ ไม่มี refresh_token ต้องทำ OAuth flow ก่อน")

    path = "/api/v2/auth/access_token/get"
    timestamp = int(time.time())
    sign = generate_sign(path, timestamp)
    url = f"https://partner.shopeemobile.com{path}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={sign}"

    body = {
        "partner_id": int(PARTNER_ID),
        "shop_id": SHOP_ID,
        "refresh_token": refresh_token_value
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, data=json.dumps(body))
    data = resp.json()
    
    if "access_token" not in data or "refresh_token" not in data:
        raise ValueError(f"❌ Refresh failed: {data}")

    save_token(data["access_token"], data["refresh_token"], data["expire_in"])
    print("✅ Shopee token refreshed successfully")
    return load_token()

# ===================== EXAMPLE =====================
if __name__ == "__main__":
    token_info = refresh_token_if_needed()
    print("🔑 Access token:", token_info["access_token"])
    print("🔑 Refresh token:", token_info["refresh_token"])
