##ใช้เรียกดู info ของแอป Shopee ใช้ได้path = "/api/v2/shop/get_shop_info"


import time, hmac, hashlib, requests, datetime,json
# from utils.token_manager import get_latest_token

from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
partner_id = 2012650
partner_key = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
shop_id = 57360480
access_token = "4d6c69445246576a535a615865644951"
# ======= ฟังก์ชันสร้าง sign =======
def shopee_generate_sign(path, timestamp, shop_id, access_token ):
    print(">>> DEBUG shop_id param:", shop_id)
    print(">>> DEBUG access_token param:", access_token)
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
  
    print("BASE STRING:", base_string)
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    print("BASE STRING:", base_string)
    print("GENERATED SIGN:", sign)  # ดู sign ที่สร้าง
    return sign





def get_shop_info():
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())

    sign = shopee_generate_sign(path, timestamp, SHOPEE_SHOP_ID, access_token)

    # ✅ ใส่ param ลงใน query string ตาม Shopee API ต้องการ
    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?partner_id={SHOPEE_PARTNER_ID}"
        f"&timestamp={timestamp}"
        f"&access_token={access_token}"
        f"&shop_id={SHOPEE_SHOP_ID}"
        f"&sign={sign}"  # 🟡 อาจใส่ sign ไปใน query ด้วย (ขึ้นกับ endpoint)
    )

    headers = {
        "Content-Type": "application/json"
    }

    # ❌ Shopee endpoint นี้ ไม่ต้องการ body -> ลองส่งเป็น empty dict
    response = requests.get(url, headers=headers)  # ✅ ใช้ GET ตาม Shopee doc

    print("=== RESPONSE ===")
    print(response.status_code)
    print(response.text)
# === RUN ===
get_shop_info()
