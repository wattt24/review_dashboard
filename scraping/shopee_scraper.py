# scraping/shopee_scraper.py

import requests
import time
import hashlib
import hmac
import pymysql
from datetime import datetime
from utils.config import (
    SHOPEE_PARTNER_ID,
    SHOPEE_PARTNER_KEY,
    SHOPEE_SHOP_ID,
    SHOPEE_ACCESS_TOKEN,
    MYSQL_HOST,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DB,
)

def fetch_shopee_ratings(product_id, limit=20, offset=0):
    """
    ดึงรีวิวสินค้าจาก Shopee OpenAPI
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

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get("data", {}).get("ratings", [])

def save_reviews_to_db(reviews, product_name="Unknown", platform="Shopee"):
    """
    บันทึกรีวิวลง MySQL
    """
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

        review_date = datetime.fromtimestamp(review_date_unix).strftime("%Y-%m-%d")

        cursor.execute(
            """
            INSERT INTO reviews
            (product_name, platform, rating, review_text, review_date, author, sentiment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                product_name,
                platform,
                rating,
                review_text,
                review_date,
                author,
                "unknown",  # รอวิเคราะห์ sentiment ต่อไป
            ),
        )

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    # ทดสอบดึงและบันทึกรีวิว
    PRODUCT_ID = "1234567890"  # แก้เป็นรหัสสินค้าจริง
    PRODUCT_NAME = "Shower Head 5-in-1"

    reviews = fetch_shopee_ratings(PRODUCT_ID)
    print(f"ดึงรีวิวมาได้ {len(reviews)} รายการ")

    if reviews:
        save_reviews_to_db(reviews, product_name=PRODUCT_NAME, platform="Shopee")
        print("บันทึกรีวิวลงฐานข้อมูลสำเร็จ")
    else:
        print("ไม่มีรีวิวให้บันทึก")
