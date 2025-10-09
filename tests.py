# import time, datetime
# import hmac
# import hashlib
# import requests

# # ======= ข้อมูลของคุณ =======
# partner_id = 2012650
# partner_key = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
# shop_id = 57360480
# access_token = "4c6d457a727a525255626d6f4c515050"
# from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
# # ======= ฟังก์ชันสร้าง sign =======
# def shopee_generate_sign(path, timestamp, shop_id, access_token ):
#     print(">>> DEBUG shop_id param:", shop_id)
#     print(">>> DEBUG access_token param:", access_token)
#     base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"
  
#     print("BASE STRING:", base_string)
#     sign = hmac.new(
#         SHOPEE_PARTNER_SECRET.encode("utf-8"),
#         base_string.encode("utf-8"),
#         hashlib.sha256
#     ).hexdigest()
#     print("BASE STRING:", base_string)
#     print("GENERATED SIGN:", sign)  # ดู sign ที่สร้าง
#     return sign

# # ======= เรียก API =======
# path = "/api/v2/product/get_item_list"
# timestamp = int(time.time())

# # เรียกใช้ฟังก์ชัน generate sign
# sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

# url = (
#     f"https://partner.shopeemobile.com{path}"

#     f"?access_token={access_token}"
#     f"&partner_id={partner_id}"
#     f"&shop_id={shop_id}"
#     f"&timestamp={timestamp}"
#     f"&sign={sign}"
# )

# print("Base string:", f"{partner_id}{path}{timestamp}{access_token}{shop_id}")
# print("Sign:", sign)
# print("URL:", url)
# print("timestamp:", timestamp)
# print("human time:", datetime.datetime.fromtimestamp(timestamp))

# response = requests.get(url)
# print(response.json())
