#services/woocommerce_service.py
import requests
from requests.auth import HTTPBasicAuth
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# โหลด .env
load_dotenv()

WOOCOMMERCE_URL = os.getenv("WOOCOMMERCE_URL")
WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")
WOOCOMMERCE_BASE_URL = os.getenv("WOOCOMMERCE_BASE_URL")
def fetch_products(per_page=20, timeout=15):
    print("✅ เริ่ม fetch_products()55555")  # DEBUG
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products"
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)

    try: 
        response = requests.get(
            url,
            auth=auth,
            params={"per_page": per_page},
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        print("⏱️ Timeout: เซิร์ฟเวอร์ใช้เวลานานเกินไป")
        return []
    except Exception as e:
        print(f"❌ ดึงข้อมูลสินค้าไม่สำเร็จ99999: {e}")
        return []


def fetch_product_sales(per_page=100, timeout=15):#วิเคราะห์ยอดขายรายสินค้า
    print("✅ เริ่ม fetch_product_sales()")
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)

    try:
        response = requests.get(
            url,
            auth=auth,
            params={"per_page": per_page, "status": "completed"},  # เฉพาะออเดอร์ที่จบแล้ว
            timeout=timeout
        )
        response.raise_for_status()
        orders = response.json()

        # รวมยอดขายตามสินค้า
        product_sales = {}
        for order in orders:
            for item in order.get("line_items", []):
                product_name = item.get("name")
                quantity = item.get("quantity", 0)
                total = float(item.get("total", 0.0))

                if product_name not in product_sales:
                    product_sales[product_name] = {"quantity": 0, "revenue": 0.0}
                product_sales[product_name]["quantity"] += quantity
                product_sales[product_name]["revenue"] += total

        return product_sales

    except requests.exceptions.Timeout:
        print("⏱️ Timeout: เซิร์ฟเวอร์ใช้เวลานานเกินไป")
        return {}
    except Exception as e:
        print(f"❌ ดึงข้อมูลยอดขายสินค้าไม่สำเร็จ:3333 {e}")
        return {}
