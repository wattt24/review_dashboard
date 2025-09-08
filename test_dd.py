import time, hmac, hashlib, requests
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_SECRET,
    SHOPEE_PARTNER_KEY,       # <-- เพิ่ม key สำหรับ sandbox
    SHOPEE_REDIRECT_URI,
    SHOPEE_SHOP_ID)

partner_id = SHOPEE_PARTNER_ID
partner_key = SHOPEE_PARTNER_KEY
shop_id = SHOPEE_SHOP_ID
code = "645159646e5568434d6b494a6c4d6542"

timestamp = int(time.time())
path = "/api/v2/auth/token/get"

base_string = f"{partner_id}{path}{timestamp}"
sign = hmac.new(
    partner_key.encode("utf-8"),
    base_string.encode("utf-8"),
    hashlib.sha256
).hexdigest()

url = f"https://partner.test-stable.shopeemobile.com{path}?partner_id={partner_id}&timestamp={timestamp}&sign={sign}"

payload = {
    "code": code,
    "shop_id": shop_id,
    "partner_id": partner_id
}

print("DEBUG ===")
print("timestamp:", timestamp)
print("base_string:", base_string)
print("sign:", sign)
print("url:", url)
print("payload:", payload)

resp = requests.post(url, json=payload)
print("response:", resp.text)

