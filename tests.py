# api/shopee_api.py
import datetime
import time, hmac, hashlib, requests, json
import urllib.parse
from utils.config import (SHOPEE_PARTNER_ID, SHOPEE_PARTNER_SECRET, SHOPEE_SHOP_ID)
from utils.token_manager import get_latest_token
from database.all_database import save_reviews_to_db
import time, datetime

# ===== Helper สำหรับดึง token จาก Google Sheet =====
def get_shopee_access_token(shop_id: str, force_refresh: bool = False):
    """
    ดึง access_token จาก Google Sheet และ auto-refresh ถ้าจำเป็น
    """
    token = get_latest_token("shopee", shop_id)
    if token:
        return token
    # fallback กรณี refresh ไม่สำเร็จ → ดึง token ล่าสุดที่บันทึกไว้
    token_data = get_latest_token("shopee", shop_id)
    return token_data["access_token"] if token_data else None


# ======= ฟังก์ชันสร้าง sign =======
def shopee_generate_sign(path, timestamp, shop_id, access_token ):
    # print(">>> DEBUG shop_id param:", shop_id)
    # print(">>> DEBUG access_token param:", access_token)
    base_string = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}"

    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        base_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    # print("BASE STRING:", base_string)
    # print(" SIGN:", sign)  # ดู sign ที่สร้าง
    return sign

# ใช้เรียกดูรายละเอียดร้านได้แล้ว
def get_shopee_shop_info(shop_id): #    get_shopee_shop_info(SHOPEE_SHOP_ID)
    """
    ดึงข้อมูลร้านจาก Shopee API
    """
    token_data = get_latest_token("shopee", shop_id)
    if not token_data:
        raise ValueError("❌ ไม่พบ Shopee access_token")
    access_token = token_data["access_token"]
    path = "/api/v2/shop/get_shop_info"
    timestamp = int(time.time())

    # สร้าง sign
    sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

    # ประกอบ URL เรียก API
    url = (
        f"https://partner.shopeemobile.com{path}"
        f"?access_token={access_token}"
        f"&partner_id={SHOPEE_PARTNER_ID}"
        f"&shop_id={shop_id}"
        f"&timestamp={timestamp}"
        f"&sign={sign}"
    )

    print("🔹 Base string:", f"{SHOPEE_PARTNER_ID}{path}{timestamp}{access_token}{shop_id}")
    print("🔹 Sign:", sign)
    print("🔹 URL:", url)
    print("🔹 Timestamp:", timestamp)
    print("🔹 Human time:", datetime.datetime.fromtimestamp(timestamp))

    # เรียก API
    response = requests.get(url)
    data = response.json()

    print("\n📦 Shopee Shop Info Response:")
    print(data)

    return data
# ใช้ได้ เรียกดู global ของ Shopee
def shopee_get_categories(shop_id, language="en"):
    path = "/api/v2/product/get_category"
    base_url = "https://partner.shopeemobile.com"
    timestamp = int(time.time())

    token_data = get_latest_token("shopee", shop_id)
    if not token_data:
        raise ValueError("❌ ไม่พบ Shopee access_token")
    access_token = token_data["access_token"]

    shop_id = int(shop_id)
    sign = shopee_generate_sign(path, timestamp, shop_id, access_token)

    params = {
        "partner_id": SHOPEE_PARTNER_ID,
        "timestamp": timestamp,
        "access_token": access_token,
        "shop_id": shop_id,
        "sign": sign,
        "language": language
    }

    url = f"{base_url}{path}"
    response = requests.get(url, params=params)
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)) 
    return response.json()


# สามารถเรียกไม่ได้ API ได้ดังนี้
# # เดิมใช้
# # params = {
# #     "partner_id": partner_id,
# #     "timestamp": timestamp,
# #     "shop_id": shop_id,
# #     "access_token": access_token,
# #     "sign": sign
# # }
# เปลี่ยนและใช้ได้

# params = {
#     "partner_id": partner_id,
#     "timestamp": timestamp,
#     "shop_id": shop_id,
#     "access_token": access_token,
#     "sign": sign,
#     "offset": 0,
#     "page_size": 20,
#     "item_status": ["NORMAL"]
#     # "item_status": ["NORMAL", "UNLIST"]
# }



# ======= เรียก API =======
def shopee_get_items_list():
    path = "/api/v2/product/get_item_list"
    timestamp = int(time.time())
    token_data = get_latest_token("shopee", SHOPEE_SHOP_ID)
    access_token = token_data.get("access_token") if token_data else None
    if not access_token:
        raise Exception("❌ ไม่พบ access_token สำหรับ Shopee shop_id นี้")
    # เรียกใช้ฟังก์ชัน generate sign
    sign = shopee_generate_sign(path, timestamp, SHOPEE_SHOP_ID, access_token)

    url = f"https://partner.shopeemobile.com{path}"

    all_items = []
    offset = 0
    page_size = 20  # ดึงได้สูงสุด 100 รายการต่อหน้า

    while True:
        timestamp = int(time.time())
        sign = shopee_generate_sign(path, timestamp, SHOPEE_SHOP_ID, access_token)

        params = {
            "partner_id": SHOPEE_PARTNER_ID,
            "timestamp": timestamp,
            "shop_id": SHOPEE_SHOP_ID,
            "access_token": access_token,
            "sign": sign,
            "offset": offset,
            "page_size": page_size,
            "item_status": ["NORMAL"]
        }

        response = requests.get(url, params=params)
        data = response.json() # แสดง response  แปลง Response object เป็น dict

        # ✅ ต้องอยู่ก่อน print
        items = data.get("response", {}).get("item", [])

        print(f"Offset: {offset}")
        print(f"จำนวน items ที่ได้: {len(items)}")
        print(f"has_next_page: {data.get('response', {}).get('has_next_page')}")
        print(f"total_count: {data.get('response', {}).get('total_count')}")

        all_items.extend(items)

        print(f"✅ ดึงข้อมูล offset {offset} ได้ {len(items)} รายการ")

        if not data.get("response", {}).get("has_next_page", False):
            break

        offset = data.get("response", {}).get("next_offset", 0)
        time.sleep(1)  # ป้องกัน rate limit

        print(f"status code: {requests.get(url, params=params).status_code}")
        print("ตัวอย่างการแสดงผลจาก response.json() ")
        print("---------------------แบบที่ 1---------------------")
        items = response.json().get("response", {}).get("item", [])
        for i, item in enumerate(items, 1):
            print(f"{i}. item_id: {item['item_id']} | status: {item['item_status']} | updated: {datetime.datetime.fromtimestamp(item['update_time'])}")
        print("----------------------     --------------------")
        # print("---------------------แบบที่ 2 ---------------------")
        # print("แสดง response แบบข้อมูลดิบ ข้อมูลชนิด Python dictionary (dict)")
        # print(response.json())
        # print("----------------------     --------------------")

        # print("---------------------แบบที่ 3 ---------------------")
   

        # print(json.dumps(data, indent=2, ensure_ascii=False))      # data = response.json()  
        # print("----------------------     --------------------")
    return all_items
def get_shopee_comments(item_id=None, comment_id=None, page_size=50):
    url = "https://partner.shopeemobile.com/api/v2/product/get_comment"
    path = "/api/v2/product/get_comment"
    comments = []
    cursor = ""
    token_data = get_latest_token("shopee", SHOPEE_SHOP_ID)
    access_token = token_data.get("access_token") if token_data else None
    if not access_token:
        raise Exception("❌ ไม่พบ access_token สำหรับ Shopee shop_id นี้")
    while True:
        timestamp = int(time.time())
        sign = shopee_generate_sign(path, timestamp, SHOPEE_SHOP_ID, access_token)

        params = {
            "partner_id": SHOPEE_PARTNER_ID,
            "shop_id": SHOPEE_SHOP_ID,
            "access_token": access_token,
            "timestamp": timestamp,
            "sign": sign,
            "cursor": cursor,
            "page_size": page_size
        }

        if item_id:
            params["item_id"] = item_id
        if comment_id:
            params["comment_id"] = comment_id

        response = requests.get(url, params=params)
        data = response.json()

        if "response" not in data or "item_comment_list" not in data["response"]:
            break

        batch = data["response"]["item_comment_list"]
        comments.extend(batch)

        # เช็คว่ามีหน้าต่อหรือไม่
        cursor = data["response"].get("next_cursor", "")
        if not cursor:
            break

        time.sleep(1)  # กัน rate limit

    return comments

def shopee_get_all_comments_from_items_list():
    """
    ดึง item_id ทั้งหมดจาก Shopee → แล้วดึง comment ของแต่ละ item_id → รวมผลลัพธ์ทั้งหมดจาก get_shopee_comments
    """
    print("🚀 เรียกใช้ shopee_get_items_list เพื่อดึงสินค้า...")
    all_items = shopee_get_items_list()  # ✅ เรียกใช้ฟังก์ชันเดิม

    if not all_items:
        print("❌ ไม่พบสินค้าใด ๆ จาก Shopee")
        return []

    all_comments = []

    print(f"📦 พบสินค้า {len(all_items)} รายการ → เริ่มดึงคอมเมนต์ของแต่ละ item...")
    for index, item in enumerate(all_items, start=1):
        item_id = item.get("item_id")
        if not item_id:
            print(f"⚠️ item ไม่มี item_id ข้ามรายการนี้ไป")
            continue

        print(f"🔎 ({index}/{len(all_items)}) กำลังดึง comment ของ item_id: {item_id}")
        try:
            comments = get_shopee_comments(item_id=item_id)

            if comments:
                # เพิ่ม item_id เข้าไปในแต่ละ comment (ถ้ายังไม่มี)
                for c in comments:
                    c["item_id"] = item_id

                all_comments.extend(comments)
                print(f"✅ ดึงได้ {len(comments)} comments จาก item_id {item_id}✅")
                print(json.dumps(comments, indent=2, ensure_ascii=False))
            else:
                print(f"⚠️ ไม่มี comment สำหรับ item_id {item_id}")

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดขณะดึง comment ของ item_id {item_id}: {e}")

        time.sleep(1)  # ป้องกัน Rate Limit

    print(f"\n🎯 รวมคอมเมนต์ทั้งหมด {len(all_comments)} รายการ จาก {len(all_items)} สินค้า")
    
    return all_comments
def shopee_forward_get_all_reviews_comments_save_to_db(): # shopee_forward_get_all_reviews_comments_save_to_db()
    """
   รวมฟังก์ชันดึงreviews_commentsee → วิเคราะห์ → บันทึกลงฐานข้อมูล
    """
    print("🚀 เริ่มดึงสินค้าจาก Shopee...")
    all_comments = shopee_get_all_comments_from_items_list()  # ดึงคอมเมนต์ทั้งหมด

    if not all_comments:
        print("❌ ไม่พบคอมเมนต์จาก Shopee")
        return

    # แปลงข้อมูลให้อยู่ในรูปแบบที่ save_reviews_to_db ใช้ได้
    formatted_reviews = []
    for c in all_comments:
        review_id = str(c.get("comment_id"))
        review_text = c.get("comment", "")
        rating = c.get("rating_star", None)
        item_id = c.get("item_id", None)
        # ใช้เวลาโพสต์ (ถ้ามี)
        ts = c.get("create_time")
        if ts:
            review_date = datetime.datetime.fromtimestamp(ts)

        else:
            review_date = datetime.now()

        formatted_reviews.append({
            "id": review_id,
            "review": review_text,
            "rating": rating,
            "product_id": item_id,
            "date_created": review_date
        })

    # ✅ เรียกฟังก์ชันบันทึกลงฐานข้อมูล
    save_reviews_to_db(formatted_reviews, platform="shopee", shop_id=str(SHOPEE_SHOP_ID))
    print("🎯 ดึงและบันทึกรีวิว Shopee สำเร็จ!")



# เรียกใช้งานตรงนี้ได้เลย
if __name__ == "__main__":
    shopee_forward_get_all_reviews_comments_save_to_db()  # เรียบร้อย
