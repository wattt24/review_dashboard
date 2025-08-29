
# scraping/fujikaservice_scraper.py
import requests
from utils.config import FUJIKA_SERVICE_SITE_URL, FUJIKA_SERVICE_CONSUMER_KEY, FUJIKA_SERVICE_CONSUMER_SECRET
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# def fetch_service_all_products(per_page=100, timeout=15, max_pages=50):
#     """
#     ดึงข้อมูลสินค้า WooCommerce
#     """
#     auth = HTTPBasicAuth(FUJIKA_SERVICE_CONSUMER_KEY, FUJIKA_SERVICE_CONSUMER_SECRET)
#     url = f"{FUJIKA_SERVICE_SITE_URL}/wp-json/wc/v3/products"

#     all_products = []
#     page = 1

#     while True:
#         resp = requests.get(url, auth=auth, params={"per_page": per_page, "page": page}, timeout=timeout)
#         resp.raise_for_status()
#         products = resp.json()

#         if not products:
#             break

#         for p in products:
#             image_url = p.get("images", [{}])[0].get("src", "")
#             all_products.append({
#                 "id": p.get("id"),
#                 "name": p.get("name"),
#                 "price": float(p.get("price") or 0),
#                 "image_url": image_url,
#                 "stock_quantity": p.get("stock_quantity", 0),
#                 "average_rating": float(p.get("average_rating", "0") or 0),
#                 "rating_count": p.get("rating_count", 0),
#                 "quantity_sold": 0,
#                 "total_revenue": 0.0
#             })

#         if len(products) < per_page or page >= max_pages:
#             break
#         page += 1

#     return all_products
def fetch_service_all_products(per_page=100, page=1, timeout=10):
    url = "https://www.fujikaservice.com/wp-json/wc/v3/products"
    auth = (FUJIKA_SERVICE_CONSUMER_KEY, FUJIKA_SERVICE_CONSUMER_SECRET)

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        resp = session.get(url, auth=auth, params={"per_page": per_page, "page": page}, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching products:", e)
        return []  # ถ้า connect ไม่ได้ ให้ return list ว่าง

# -------------------- ดึง feedback / คำติชม --------------------
# -------------------- ฟังก์ชันรวมเรียกใช้งาน --------------------
# -------------------- ดึง Feedback --------------------
# def fetch_service_feedback():
#     """
#     ดึง Feedback / คำติชมจาก REST API ของ fujikaservice.com
#     คืนค่าเป็น list ของ dict
#     """
#     url = "https://fujikaservice.com/wp-json/wc/v3/feedback"
#     headers = {
#         "Authorization": f"Bearer {FUJIKA_SERVICE_CONSUMER_SECRET,WOOCOMMERCE_CONSUMER_KEY}",
#         "Accept": "application/json"
#     }
#     try:
#         r = requests.get(url, headers=headers, timeout=10)
#         r.raise_for_status()
#         return r.json()  # คืนค่า list ของ feedback
#     except requests.RequestException as e:
#         print(f"Error fetching feedback: {e}")
#         return []

# # -------------------- ดึง Tickets --------------------
# def fetch_service_tickets():
#     """
#     ดึงข้อมูล Tickets / งานบริการ
#     """
#     url = "f{FUJIKA_SERVICE_SITE_URL}/wp-json/fujikaservice/v1/tickets"
#     headers = {
#         "Authorization": f"Bearer {FUJIKA_SERVICE_CONSUMER_SECRET}",
#         "Accept": "application/json"
#     }
#     try:
#         r = requests.get(url, headers=headers, timeout=10)
#         r.raise_for_status()
#         return r.json()
#     except requests.RequestException as e:
#         print(f"Error fetching tickets: {e}")
#         # fallback ถ้า API ไม่คืนค่า
#         return [
#             {"ticket_id": 1, "status": "open", "subject": "แจ้งซ่อมสินค้า"},
#             {"ticket_id": 2, "status": "closed", "subject": "ขอใบรับประกัน"},
#         ]

# # -------------------- ดึง Products --------------------


# -------------------- ฟังก์ชันรวม --------------------
# def fetch_all_service_data():
    # """
    # ดึงข้อมูลทั้งหมด: feedback + tickets + products
    # """
    # feedback = fetch_service_feedback()
    # tickets = fetch_service_tickets()
    # products = fetch_service_all_products()

    # print(f"✅ ดึงข้อมูลสำเร็จ: {len(feedback)} feedback, {len(tickets)} tickets, {len(products)} products")
    # return {
    #     "feedback": feedback,
    #     "tickets": tickets,
    #     "products": products
    # }