import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import sys
import os
import datetime
from datetime import datetime
os.environ["GOOGLE_SHEET_ID"] = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"
import time
from utils.token_manager import get_latest_token, save_token
# from utils.config import LAZADA_APP_ID, LAZADA_APP_SECRET
import requests
# ****************************ใช้ได้
from lazop.base import LazopClient, LazopRequest
import json
# ====== ตั้งค่าพื้นฐาน (ควรเก็บไว้ในที่ปลอดภัย ไม่ใช่ในโค้ด) ======
# ค่าเหล่านี้เป็นตัวอย่าง ซึ่งอาจไม่ถูกต้องในความเป็นจริง และควรเก็บไว้เป็นความลับ
LALA=100200610
LAZADA_APP_ID = "135259"
LAZADA_APP_SECRET = "MXZ9vzVVw3TsGbal73a3PljVprysSRrN" 
# LAZADA_ACCESS_TOKEN = "50000300c32t6FEoxrr98dk0ejxhvvjcjCSesUzFflPL153b42e63GwXGwiEvSgU"
import time, json
from datetime import datetime
from database.all_database import save_reviews_to_db, get_connection 
import json
import requests
import time
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta, timezone


import time
from lazop.base import LazopClient, LazopRequest
# # ตัวกลาง sdk ในการเรียก Lazada API

# 
def call_lazada_api(endpoint, method="GET", params=None, access_token=None):
    """
    เรียก Lazada API ผ่าน SDK
    ถ้า access_token มีอยู่ จะไม่ไปดึงจาก Google Sheet
    """
    try:
        if not access_token:
            # ถ้าไม่มี token ให้ดึงจาก Google Sheet
            token_data = get_latest_token("lazada", LALA)  # หรือ account_id ของคุณ
            if not token_data or not token_data.get("access_token"):
                raise ValueError("❌ ไม่พบ Lazada access_token ใน Google Sheet")
            access_token = token_data["access_token"]

        client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
        request = LazopRequest(endpoint, method)

        if params:
            for k, v in params.items():
                request.add_api_param(k, str(v))

        response = client.execute(request, access_token)

        if isinstance(response.body, (str, bytes)):
            data = json.loads(response.body)
        else:
            data = response.body

        return data

    except Exception as e:
        print(f"❌ Error calling Lazada API: {str(e)}")
        return {"error": str(e)}

# ====== ฟังก์ชันย่อยเฉพาะ ======

def lazada_get_products(offset=0, limit=10):
    """
    ดึงรายการสินค้าในร้าน
    """
    return call_lazada_api(
        endpoint="/products/get",
        method="GET",
        params={
            "offset": offset,
            "limit": limit
        }
    )  #ย้ายใส่ของจริงแล้ว
def lazada_get_active_item_ids(limit=50, filter_status="live"):
    """ดึงเอา item_id เฉพาะสินค้าที่ Active (live status)"""
    all_item_ids = []
    offset = 0

    while True:
        response = call_lazada_api(
            endpoint="/products/get",
            method="GET",
            params={
                "offset": offset,
                "limit": limit,
                "filter": filter_status  # ใช้ค่าเดียวเท่านั้น
            }
        )

        # ✅ ตรวจสอบ rate limit
        if response.get("code") == "ApiCallLimit":
            print(f"⚠️ Rate limit เจอ! รอ 2 วินาทีแล้วลองใหม่…")
            time.sleep(2)
            continue  # ลองเรียก API เดิมซ้ำ

        # ตรวจสอบ error อื่น
        if not response or response.get("code") != "0":
            print("❌ Error:", response)
            break

        products = response["data"].get("products", [])
        if not products:
            break

        # ดึง item_id ทั้งหมด
        item_ids = [p["item_id"] for p in products]
        all_item_ids.extend(item_ids)

        print(f"📦 ดึงข้อมูล {len(products)} รายการ | offset={offset}")

        if len(products) < limit:
            break

        offset += limit
        time.sleep(1) # เว้นระยะเล็กน้อยป้องกัน rate limit
    print("\n✅ รวมสินค้าที่ Active ทั้งหมด:", len(all_item_ids))
    print("🆔 item_id ทั้งหมด:", all_item_ids)
    return all_item_ids


def get_review_id_list(item_id, days_back=7, offset_days=0, page=1, access_token=None, max_retries=5):
    """ดึง review ID ของสินค้า Lazada พร้อม handle rate limit"""
    end_time = int(time.time() * 1000) - (offset_days * 24 * 60 * 60 * 1000)  # ✅ เลื่อนช่วงเวลาออกไป
    start_time = end_time - (days_back * 24 * 60 * 60 * 1000)
    retry_count = 0
    wait_time = 2  # เริ่มต้นรอ 2 วินาที (จะเพิ่มขึ้นเรื่อย ๆ หากเจอ rate limit)

    while retry_count < max_retries:
        response = call_lazada_api(
            endpoint="/review/seller/history/list",
            method="GET",
            params={
                "item_id": item_id,
                "start_time": start_time,
                "end_time": end_time,
                "current": page
            },
            access_token=access_token
        )

        print(f"🆔 Request ID: {response.get('request_id', 'ไม่มีข้อมูล')}")

        # ✅ ตรวจเจอ rate limit → รอแล้วลองใหม่
        if response and response.get("code") == "ApiCallLimit":
            print(f"⚠️ Rate limit เจอ! รอ {wait_time} วินาทีแล้วลองใหม่...")
            time.sleep(wait_time)
            retry_count += 1
            wait_time *= 2  # เพิ่มเวลารอเป็น 2x (2→4→8→16...)
            continue

        # ✅ ตรวจ error อื่น
        if not response or response.get("code") != "0" or not response.get("success"):
            print("❌ Error fetching review ID list:", response)
            return [], response
        time.sleep(0.2)
        # ✅ ได้ผลลัพธ์ปกติ
        data = response.get("data", {})
        review_ids = data.get("id_list", [])
        time.sleep(8)
        if review_ids:
            print("🆔 item_id คือ", item_id)
            print(f"✅ พบ Review ID {len(review_ids)} รายการ:", review_ids)
        else:
            print("⚠️ ไม่มี Review ID ในหน้านี้")

        return review_ids, response

    # ❌ ถ้าลองครบแล้วแล้วยังเจอ rate limit
    print(f"❌ เกินจำนวน retry ที่กำหนด ({max_retries} ครั้ง) ข้าม item_id {item_id}")
    return [], {"error": "ApiCallLimit after max retries"}



def get_all_review_ids_by_item_id(item_id, days_back=7, offset_days=0, access_token=None):
    """ วนลูปทุกหน้า get_review_id_list จนครบทุกรีวิวของ item_id """
    all_review_ids = []
    page = 1

    while True:
        review_ids, response = get_review_id_list(
            item_id,
            days_back=days_back,
            offset_days=offset_days,  # ✅ ส่ง offset_days เข้าไปจริง ๆ
            page=page,
            access_token=access_token
        )

        if response.get('code') == 'ApiCallLimit':
            wait_time = 2
            print(f"⚠️ Rate limit เจอ! รอ {wait_time} วินาที...")
            time.sleep(wait_time)
            continue

        if not review_ids:
            break

        all_review_ids.extend(review_ids)
        page += 1

        time.sleep(2)

    print(f"รวม Review ทั้งหมดของ item_id {item_id}: {len(all_review_ids)} รายการ")
    print("🆔 Review ID ทั้งหมด:", all_review_ids)
    return all_review_ids


def get_review_details_by_ids(review_id_list):
    """
    ดึงรายละเอียดรีวิวจาก Lazada API (/review/seller/list/v2)
    โดยใช้ review_id_list ที่ได้จาก /review/seller/history/list
    """
    if not review_id_list:
        print("⚠️ ไม่มี Review ID ให้ดึงรายละเอียด")
        return []

    print(f"📥 กำลังดึงรายละเอียดรีวิวทั้งหมด ({len(review_id_list)} รายการ)...")

    response = call_lazada_api(
        endpoint="/review/seller/list/v2",
        method="GET",
        params={
            "id_list": review_id_list   # ✅ ต้องส่งเป็น list
        }
    )

    print(f"🆔 Request ID: {response.get('request_id', 'ไม่มีข้อมูล')}")

    if not response or response.get("code") != "0" or not response.get("success"):
        print("❌ Error fetching review details:", response)
        return []

    data = response.get("data", {})
    reviews = data.get("review_list", [])

    if not reviews:
        print("⚠️ ไม่มีข้อมูลรีวิวใน response")
        return []
    time.sleep(1)
    print(f"✅ ได้รายละเอียดรีวิวทั้งหมด {len(reviews)} รายการ")
    print("\n🎯 รายละเอียดรีวิวดิบ ")
    print(json.dumps(reviews, indent=2, ensure_ascii=False))
    return reviews

def lazada_fetch_and_show_all_reviews_Retrieve_historical(LALA, days_back=7, num_rounds=12, limit=15):
    """
    ดึงรีวิวสินค้าจาก Lazada แบบย้อนหลังหลายรอบ
    เช่น days_back=7, num_rounds=12  → ดึงย้อนหลัง 12 รอบ (7 วันต่อรอบ = 84 วัน)
    """
    import json, time
    from datetime import datetime, timedelta, timezone
    from database.all_database import save_reviews_to_db

    print(f"🚀 เริ่มดึงรีวิว Lazada ย้อนหลัง {num_rounds} รอบ (รอบละ {days_back} วัน)")

    # ✅ ดึง token ล่าสุด
    token_data = get_latest_token("lazada", LALA)
    access_token = token_data["access_token"]

    # ✅ ดึงสินค้าทั้งหมด
    all_items = lazada_get_active_item_ids(limit=limit)
    total_all_reviews = []

    # 🔁 วนรอบย้อนหลัง
    for round_num in range(num_rounds):
        offset_days = round_num * days_back
        print(f"\n⏮️ รอบที่ {round_num + 1}/{num_rounds} → ย้อนหลัง {offset_days}-{offset_days + days_back} วัน")

        items_with_reviews = {}
        total_reviews = 0

        # ดึง review_id ของแต่ละสินค้าในรอบนี้
        for item_id in all_items:
            all_reviews = get_all_review_ids_by_item_id(
                item_id,
                days_back=days_back,
                offset_days=offset_days,
                access_token=access_token
            )

            if all_reviews:
                items_with_reviews[item_id] = all_reviews
                total_reviews += len(all_reviews)

            print(f"📦 item_id {item_id} → มีรีวิว {len(all_reviews)} รายการ")
            time.sleep(2)

        # รวม review_id ทั้งหมดของรอบนี้
        all_review_ids_flat = [rid for ids in items_with_reviews.values() for rid in ids]
        print(f"✅ รวมทั้งหมด {len(all_review_ids_flat)} รีวิวจาก {len(items_with_reviews)} สินค้า (รอบที่ {round_num+1})")
        print( items_with_reviews)


        # ดึงรายละเอียดรีวิวทั้งหมด
        
        review_details = get_review_details_by_ids(all_review_ids_flat)
        formatted_reviews = []

        for r in review_details:
            # ✅ แปลง timestamp → datetime (โซนไทย +7)
            timestamp = r.get("create_time") or r.get("submit_time")
            if timestamp:
                try:
                    date_created = (
                        datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc) + timedelta(hours=7)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"⚠️ แปลงเวลาไม่ได้สำหรับ review_id {r.get('id')}: {e}")
                    date_created = None
            else:
                date_created = None

            formatted_reviews.append({
                "id": r["id"],  # ✅ เปลี่ยนจาก review_id → id
                "review": r.get("review_content") or r.get("review"),  # ✅ เปลี่ยนจาก review_content → review
                "date_created": date_created,
                "rating": r.get("product_rating") or r.get("ratings", {}).get("product_rating"),
                "product_id": r.get("product_id") or r.get("item_id")
            })

        save_reviews_to_db(
            reviews=formatted_reviews,
            platform="lazada",
            shop_id=str(LALA)
        )
        print(f"💾 บันทึกแล้ว {len(formatted_reviews)} รีวิว (รอบที่ {round_num+1})")
 
        total_all_reviews.extend(formatted_reviews)

        # ป้องกัน rate limit
        time.sleep(2)

    # 🔚 สรุปรวมทั้งหมด
    print(f"\n🎯 รวมทั้งหมด {len(total_all_reviews)} รีวิว จาก {num_rounds} รอบ ถูกบันทึกลงฐานข้อมูลแล้ว!")
    print("\n🎯 n🎯 รายละเอียดรีวิวทั้งหมด1111111111 (รวมทุกช่วง)")
    print(json.dumps(total_all_reviews, indent=2, ensure_ascii=False))
    return total_all_reviews



def lazada_fetch_review_by_id(review_id, LALA):
    """
    ✅ ดึงรายละเอียดรีวิวจาก Lazada โดยใช้ review_id เดียว
    แล้วบันทึกลงฐานข้อมูล
    """
    print(f"🚀 กำลังดึงรายละเอียดรีวิวจาก Lazada (review_id={review_id})")

    # 1️⃣ ดึง token ล่าสุด
    token_data = get_latest_token("lazada", LALA)
    access_token = token_data["access_token"]

    # 2️⃣ เรียก Lazada API เพื่อดึงรายละเอียดรีวิว
    response = call_lazada_api(
        endpoint="/review/seller/list/v2",
        method="GET",
        params={
            "id_list": [review_id]  # ✅ Lazada ต้องการ list แม้มีแค่ 1 id
        },
        access_token=access_token
    )

    # 3️⃣ ตรวจสอบ response
    if not response or response.get("code") != "0" or not response.get("success"):
        print("❌ ไม่สามารถดึงรีวิวได้:", response)
        return None

    data = response.get("data", {})
    reviews = data.get("review_list", [])

    if not reviews:
        print("⚠️ ไม่มีรีวิวที่ตรงกับ review_id นี้")
        return None

    # 4️⃣ แปลงรูปแบบข้อมูลรีวิว
    r = reviews[0]
    timestamp = r.get("create_time") or r.get("submit_time")
    if timestamp:
        date_created = (
            datetime.fromtimestamp(int(timestamp) / 1000, tz=timezone.utc) + timedelta(hours=7)
        ).strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_created = None

    formatted_review = {
        "id": r.get("id"),
        "review": r.get("review_content") or r.get("review"),
        "date_created": date_created,
        "rating": r.get("product_rating") or r.get("ratings", {}).get("product_rating"),
        "product_id": r.get("product_id") or r.get("item_id")
    }

    # 5️⃣ แสดงผลรีวิวแบบสวย ๆ
    print("\n✅ รายละเอียดรีวิวที่ดึงได้:")
    print(json.dumps(formatted_review, indent=4, ensure_ascii=False))

    # 6️⃣ บันทึกลงฐานข้อมูล
    save_reviews_to_db(
        reviews=[formatted_review],
        platform="lazada",
        shop_id=str(LALA)
    )

    print("💾 รีวิวนี้ถูกบันทึกลงฐานข้อมูลเรียบร้อยแล้ว!")
    return formatted_review  # ตัวอย่างการเรียกใช้ lazada_fetch_review_by_id(985301659179601, LALA)
# ===== ทดสอบเรียกใช้งาน =====
if __name__ == "__main__":
    # ดึงย้อนหลัง 3 รอบ × 7 วัน = 21 วัน (ประมาณ 1 เดือน)
    # lazada_fetch_and_show_all_reviews_Retrieve_historical(LALA, days_back=7, num_rounds=3)


    # # ดึงย้อนหลัง 12 รอบ × 7 วัน = 84 วัน (ประมาณ 3 เดือน)
    lazada_fetch_and_show_all_reviews_Retrieve_historical(LALA, days_back=7, num_rounds=12)


