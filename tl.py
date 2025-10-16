import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import sys
import os
import datetime
os.environ["GOOGLE_SHEET_ID"] = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"
from utils.token_manager import get_latest_token, save_token
# from utils.config import LAZADA_APP_ID, LAZADA_APP_SECRET
import requests
# ****************************ใช้ได้
from lazop.base import LazopClient, LazopRequest
import json
# ====== ตั้งค่าพื้นฐาน (ควรเก็บไว้ในที่ปลอดภัย ไม่ใช่ในโค้ด) ======
# ค่าเหล่านี้เป็นตัวอย่าง ซึ่งอาจไม่ถูกต้องในความเป็นจริง และควรเก็บไว้เป็นความลับ
LAZADA_APP_ID = "135259"
LAZADA_APP_SECRET = "MXZ9vzVVw3TsGbal73a3PljVprysSRrN" 
LAZADA_ACCOUNT_ID = "pirattapong.v@gmail.com"
import json
import requests
import time
import hashlib
import hmac
import urllib.parse
import datetime
from lazop.base import LazopClient, LazopRequest
# # ตัวกลาง sdk ในการเรียก Lazada API
# def call_lazada_api(endpoint, method="GET", params=None):
#     """
#     ฟังก์ชันกลางสำหรับเรียก Lazada API ผ่าน SDK
#     """
#     try:
#         client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
#         request = LazopRequest(endpoint, method)

#         if params:
#             for k, v in params.items():
#                 request.add_api_param(k, str(v))

#         response = client.execute(request, LAZADA_ACCESS_TOKEN)

#         # ✅ บาง SDK จะคืน dict, บางตัวคืน string
#         if isinstance(response.body, (str, bytes)):
#             data = json.loads(response.body)
#         else:
#             data = response.body

#         return data

#     except Exception as e:
#         print(f"❌ Error calling Lazada API: {str(e)}")
#         return {"error": str(e)}

def call_lazada_api(endpoint, method="GET", params=None, account_id=LAZADA_ACCOUNT_ID):
    """
    เรียก Lazada API ผ่าน SDK
    ดึง access_token ล่าสุดจาก Google Sheet
    """
    try:
        # ดึง token ล่าสุดจาก Google Sheet
        token_data = get_latest_token("lazada", account_id)
        if not token_data or not token_data.get("access_token"):
            raise ValueError("❌ ไม่พบ Lazada access_token ใน Google Sheet")

        access_token = token_data["access_token"]

        # สร้าง client Lazop
        client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
        request = LazopRequest(endpoint, method)

        if params:
            for k, v in params.items():
                request.add_api_param(k, str(v))

        response = client.execute(request, access_token)

        # บาง SDK คืน dict, บางตัวคืน string
        if isinstance(response.body, (str, bytes)):
            data = json.loads(response.body)
        else:
            data = response.body

        return data

    except Exception as e:
        print(f"❌ Error calling Lazada API: {str(e)}")
        return {"error": str(e)}
    
def lazada_get_seller_info():
    """
    ดึงข้อมูลร้าน (Seller Info) ของบัญชีที่เชื่อมต่อไว้
    เช่น seller_id, name, email, country, shop_name ฯลฯ
    """
    response = call_lazada_api(
        endpoint="/seller/get",
        method="GET"
    )

    if not response or response.get("code") != "0":
        print("❌ Error fetching seller info:", response)
        return None

    data = response.get("data", {})
    print("✅ ข้อมูลร้าน:", json.dumps(data, indent=2, ensure_ascii=False))
    return data

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

def lazada_check_get_all_active_item_ids(limit=50):
    all_item_ids = []
    offset = 0

    while True:
        response = call_lazada_api(
            endpoint="/products/get",
            method="GET",
            params={
                "offset": offset,
                "limit": limit
            }
        )

        # ❌ ถ้ามี error ให้หยุด
        if not response or response.get("code") != "0":
            print("❌ Error:", response)
            break

        products = response["data"].get("products", [])
        if not products:
            break  # ไม่มีสินค้าแล้ว

        # ✅ ดึงเฉพาะสินค้าที่ Active
        active_items = [
            p["item_id"] for p in products
            if p.get("status") == "Active"
        ]
        all_item_ids.extend(active_items)

        print(f"📦 ดึงข้อมูล {len(products)} รายการ (Active {len(active_items)} ชิ้น) | offset={offset}")

        # ถ้าจำนวนสินค้าที่ได้ < limit แปลว่าดึงมาครบแล้ว
        if len(products) < limit:
            break

        offset += limit  # ไปหน้าถัดไป

    print("\n✅ รวมสินค้าที่ Active ทั้งหมด:", len(all_item_ids))
    print("🆔 item_id ทั้งหมด:", all_item_ids)
    return all_item_ids




def get_review_id_list(item_id, days_back=7, page=1):
    end_time = int(time.time() * 1000)
    start_time = end_time - (days_back * 24 * 60 * 60 * 1000)

    response = call_lazada_api(
        endpoint="/review/seller/history/list",
        method="GET",
        params={
            "item_id": item_id,
            "start_time": start_time,
            "end_time": end_time,
            "current": page
        }
    )

    print(f"🆔 Request ID: {response.get('request_id', 'ไม่มีข้อมูล')}")

    if not response or response.get("code") != "0" or not response.get("success"):
        print("❌ Error fetching review ID list:", response)
        return [], response

    data = response.get("data", {})
    review_ids = data.get("id_list", [])  # ✅ Lazada ใช้ id_list

    if not review_ids:
        print("⚠️ ไม่มี Review ID ในหน้านี้")
    else:
        print(f"✅ พบ Review ID {len(review_ids)} รายการ:", review_ids)

    return review_ids, response
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

    print(f"✅ ได้รายละเอียดรีวิวทั้งหมด {len(reviews)} รายการ")
    return reviews

def get_all_reviews_for_item_list(item_id_list, days_back=7):
    """
    ดึงรีวิวทั้งหมดของสินค้าหลายตัว (item_id_list)
    """
    all_reviews = []

    for item_id in item_id_list:
        print(f"\n🛒 กำลังดึงรีวิวของ item_id={item_id} ...")
        current_page = 1

        while True:
            # 1️⃣ ดึง Review ID ของหน้าปัจจุบัน
            review_ids, response = get_review_id_list(item_id, days_back=days_back, page=current_page)
            if not review_ids:
                break

            # 2️⃣ ดึงรายละเอียดรีวิวจาก ID
            reviews = get_review_details_by_ids(review_ids)
            all_reviews.extend(reviews)

            # 3️⃣ เช็คว่ามีหน้าต่อไปไหม (has_next)
            data = response.get("data", {})
            if not data.get("has_next", False):
                break

            current_page += 1

        print(f"🎯 รวมรีวิวที่ดึงได้สำหรับ item_id={item_id}: {len([r for r in all_reviews if r.get('product_id') == item_id])}")

    print(f"\n✅ รวมรีวิวทั้งหมดที่ดึงได้จากสินค้าทั้งหมด: {len(all_reviews)}")
    return all_reviews


# ==============================
# 🔹 ตัวอย่างการเรียกใช้งาน


# ===== ทดสอบเรียกใช้งาน =====
if __name__ == "__main__":
    seller_info = lazada_get_seller_info()

    if seller_info:
        print("\n🎯 รายละเอียดร้าน:")
        print("🆔 Seller ID:", seller_info.get("seller_id"))
        print("🏪 ชื่อร้าน:", seller_info.get("shop_name"))
        print("📧 อีเมล:", seller_info.get("email"))
        
    # products_response = lazada_get_products(offset=0, limit=10)
    # print(json.dumps(products_response, indent=2, ensure_ascii=False))
    # active_item_ids = lazada_check_get_all_active_item_ids(limit=50)

    # # แสดงผลลัพธ์
    # print("Active item IDs:")
    # for item_id in active_item_ids:
    #     print(item_id)

    # review_ids, response = get_review_id_list(
    #     item_id=522482835,
    #     days_back=7
    # )

    # print("\n🎯 รายการ Review ID ทั้งหมดที่ดึงได้:")
    # print(json.dumps(response, indent=2, ensure_ascii=False))  # ✅ ใช้ได้แล้ว
    # print(json.dumps(review_ids, indent=2, ensure_ascii=False))

    # review_details = get_review_details_by_ids(review_ids)

    # print("\n🎯 รายละเอียดรีวิวทั้งหมด:")
    # print(json.dumps(review_details, indent=2, ensure_ascii=False))

    # item_list = lazada_check_get_all_active_item_ids(limit=50)
    # all_reviews = get_all_reviews_for_item_list(item_list, days_back=7)  

    # print("\n🎯 รายละเอียดรีวิวทั้งหมด:")
    # for r in all_reviews:
    #     print(json.dumps(r, indent=2, ensure_ascii=False))



