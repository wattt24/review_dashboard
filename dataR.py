import requests
import pymysql
from datetime import datetime
from requests.auth import HTTPBasicAuth
from api.fujikathailand_rest_api import fetch_product_reviews
from utils.config import WOOCOMMERCE_URL, WOOCOMMERCE_CONSUMER_KEY,WOOCOMMERCE_CONSUMER_SECRET,FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS
# DB connection
conn = pymysql.connect(
    host="yamanote.proxy.rlwy.net",
    user="root",
    password="yeiIByLVJqRlPrzKLGaNCNySevvHeabG",
    port=49296,
    database="railway",
    charset="utf8mb4"
)
cursor = conn.cursor()

# # WooCommerce API
api_url = "https://www.fujikathailand.com/wp-json/wc/v3/orders?per_page=100"
auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY,WOOCOMMERCE_CONSUMER_SECRET)
response = requests.get(api_url, auth=auth)
orders = response.json()

shop_id = "website_01"  # กำหนดเองเพราะไม่มี shop_id

for order in orders:
    order_id = str(order["id"])
    order_date = order["date_created"]
    for item in order["line_items"]:
        product_id = str(item["product_id"])
        product_name = item["name"]
        quantity = item["quantity"]
        amount = item["total"]

        sql = """
        INSERT INTO sales_history (platform, shop_id, order_id, product_id, product_name, quantity, amount, order_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity=VALUES(quantity), amount=VALUES(amount)
        """
        cursor.execute(sql, ("fujikathailand", shop_id, order_id, product_id, product_name, quantity, amount, order_date))
conn.commit()
cursor.close()
conn.close()
print(f"Inserted/Updated {len(orders)} orders.")
# 111111



# WordPress API endpoint ดึงรีวิว / comments ทั่วไป
# wp_base_url = "https://www.fujikathailand.com/wp-json/wp/v2"
# api_url = f"{wp_base_url}/comments?per_page=100"

# # ใช้ Basic Auth กับ username + App Password
# auth = HTTPBasicAuth(FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS)
# response = requests.get(api_url, auth=auth)
# reviews = response.json()

# for r in reviews:
#     review_id = str(r["id"])
#     review_text = r["content"]["rendered"]
#     review_date = r["date"]

#     # สำหรับ WordPress comment ไม่มี product_id, rating, sentiment, keywords
#     product_id = None
#     rating = None
#     sentiment = None
#     keywords = None

#     sql = """
#     INSERT INTO reviews_history 
#     (platform, shop_id, product_id, review_id, rating, review_text, sentiment, keywords, review_date)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#     ON DUPLICATE KEY UPDATE review_text=VALUES(review_text)
#     """
#     cursor.execute(sql, ("fujikathailand",shop_id, product_id, review_id, rating, review_text, sentiment , keywords, review_date ))

# conn.commit()
# cursor.close()
# conn.close()

# print(f"Inserted/Updated {len(reviews)} reviews.")