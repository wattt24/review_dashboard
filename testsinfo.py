##ใช้เรียกดู info ของแอป Shopee ใช้ได้path = "/api/v2/shop/get_shop_info"


import time, hmac, hashlib, requests, datetime,json
# from utils.token_manager import get_latest_token

from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
partner_id = 2012650
partner_key = "shpk746161577650576364596f5657646c596b49705772546b4a52446a416b42"
shop_id = 57360480
access_token = "eyJhbGciOiJIUzI1NiJ9.COrrehABGOCArRsgASipnL3HBjD88e3jCzgBQAE.cYvkR8091JkyjaRCKHPT1NZI009rK13s9gdg_960Le4"
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






# item_id = 1039005306  # 🟢 item_id ที่ต้องการดูรีวิว

# timestamp = int(time.time())
# path = "/api/v2/product/get_comment"

# base_string = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
# sign = hmac.new(
#     partner_key.encode("utf-8"), base_string.encode("utf-8"), hashlib.sha256
# ).hexdigest()

# url = (
#     f"https://partner.shopeemobile.com{path}"
#     f"?access_token={access_token}"
#     f"&partner_id={partner_id}"
#     f"&shop_id={shop_id}"
#     f"&timestamp={timestamp}"
#     f"&sign={sign}"
#     f"&item_id={item_id}"
#     f"&page_size=50"
# )

# response = requests.get(url)
# data = response.json()
# print(json.dumps(data, indent=2, ensure_ascii=False))


# response = requests.get(url)
# data = response.json()

# # ======= แสดงข้อมูลร้าน =======
# print(data)

# def get_all_items():
#     path = "/api/v2/product/get_item_list"
#     all_items = []
#     offset = 0
#     page_size = 50  # Shopee อนุญาตสูงสุด 100 ต่อหน้า

#     while True:
#         timestamp = int(time.time())
#         sign = shopee_generate_sign(path, timestamp, shop_id, access_token)
#         url = (
#             f"https://partner.shopeemobile.com{path}"
#             f"?access_token={access_token}"
#             f"&partner_id={partner_id}"
#             f"&shop_id={shop_id}"
#             f"&timestamp={timestamp}"
#             f"&sign={sign}"
#             f"&item_status=NORMAL"
#             f"&offset={offset}"
#             f"&page_size={page_size}"
#         )

#         response = requests.get(url)
#         data = response.json()

#         # ตรวจสอบ error
#         if data.get("error"):
#             print(f"❌ ERROR: {data['error']} - {data['message']}")
#             break

#         response_data = data.get("response", {})
#         items = response_data.get("item", [])
#         all_items.extend(items)

#         print(f"✅ ดึงมาแล้ว {len(all_items)} / {response_data.get('total_count', '?')} รายการ")

#         if not response_data.get("has_next_page"):
#             break  # ไม่มีหน้าถัดไปแล้ว

#         offset = response_data.get("next_offset", offset + page_size)
#         time.sleep(1)  # กัน rate limit

#     return all_items
