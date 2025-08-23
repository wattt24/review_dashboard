# scraping/shopee_api.py

import requests
import time
import hashlib
import hmac
import pymysql
from datetime import datetime
from utils.config import *

access_token = shopee_auth.get_valid_access_token(shop_id)
if access_token:
    # ตัวอย่างดึง Shop Info
    path = "/api/v2/shop/get_shop_info"
    result = shopee_auth.call_shopee_api(path, access_token, shop_id)
    st.write(result)

    # ตัวอย่างดึง Orders
    path = "/api/v2/orders/get_order_list"
    params = {"page_size": 10, "time_range_field": "create_time"}
    orders = shopee_auth.call_shopee_api(path, access_token, shop_id, params)
    st.write(orders)

def fetch_shopee_ratings(product_id, limit=20, offset=0):
    """
    ดึงรีวิวสินค้าจาก Shopee OpenAPI พร้อมดัก error
    """
    partner_id = int(SHOPEE_PARTNER_ID)
    partner_key = SHOPEE_PARTNER_KEY.encode("utf-8")
    shop_id = int(SHOPEE_SHOP_ID)
    access_token = SHOPEE_ACCESS_TOKEN
    timestamp = int(time.time())

    path = "/api/v2/product/get_ratings"
    base_url = "https://partner.shopeemobile.com"
    url = base_url + path

    sign_base = f"{partner_id}{path}{timestamp}{access_token}{shop_id}"
    signature = hmac.new(partner_key, sign_base.encode("utf-8"), hashlib.sha256).hexdigest()

    params = {
        "access_token": access_token,
        "partner_id": partner_id,
        "shop_id": shop_id,
        "timestamp": timestamp,
        "sign": signature,
        "item_id": product_id,
        "offset": offset,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # ตรวจสอบว่า status code เป็น 2xx หรือไม่
        data = response.json()
        return data.get("data", {}).get("ratings", [])
    except requests.RequestException as e:
        print(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก Shopee API: {e}")
        return []
    except Exception as e:
        print(f"ข้อผิดพลาดอื่น ๆ: {e}")
        return []


def save_reviews_to_db(reviews, product_id: int, platform_id: int):
    """
    บันทึกรีวิวลง MySQL พร้อมดัก error
    """
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            charset="utf8mb4",
        )
        cursor = conn.cursor()

        for r in reviews:
            review_text = r.get("comment", "")
            rating = r.get("rating_star", 0)
            review_date_unix = r.get("ctime", 0)
            author = r.get("author_username", "")
            review_title = None
            sentiment_score = None
            review_date = datetime.fromtimestamp(review_date_unix).strftime("%Y-%m-%d %H:%M:%S")

            try:
                cursor.execute(
                    """
                    INSERT INTO reviews
                    (customer_id, product_id, platform_id, rating, review_title, review_text, review_date, sentiment_score, author)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        None,
                        product_id,
                        platform_id,
                        rating,
                        review_title,
                        review_text,
                        review_date,
                        sentiment_score,
                        author,
                    ),
                )
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการบันทึกรีวิว: {e}")
                continue

        conn.commit()
    except pymysql.MySQLError as e:
        print(f"ไม่สามารถเชื่อมต่อหรือเขียนฐานข้อมูลได้: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


if __name__ == "__main__":
    PRODUCT_ID = 1234567890  # แก้ให้ตรงกับสินค้าจริงใน Shopee
    PLATFORM_ID = 1  # สมมุติว่า Shopee มี platform_id = 1

    reviews = fetch_shopee_ratings(PRODUCT_ID)
    print(f"ดึงรีวิวมาได้ {len(reviews)} รายการ")

    if reviews:
        save_reviews_to_db(reviews, product_id=PRODUCT_ID, platform_id=PLATFORM_ID)
        print("บันทึกรีวิวลงฐานข้อมูลสำเร็จ")
    else:
        print("ไม่มีรีวิวให้บันทึก")

def get_reviews():
    """
    ดึงรีวิวจาก Shopee และบันทึกลงฐานข้อมูล
    """
    reviews = fetch_shopee_ratings(PRODUCT_ID)
    print(f"ดึงรีวิวมาได้ {len(reviews)} รายการ")

    if reviews:
        save_reviews_to_db(reviews, product_id=PRODUCT_ID, platform_id=PLATFORM_ID)
        print("บันทึกรีวิวลงฐานข้อมูลสำเร็จ")
    else:
        print("ไม่มีรีวิวให้บันทึก")


if __name__ == "__main__":
    get_reviews()