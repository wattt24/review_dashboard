import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

# โหลด .env
load_dotenv()

WOOCOMMERCE_URL = os.getenv("WOOCOMMERCE_URL")
WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")

def fetch_productss(per_page=20, timeout=15):
    print("✅ เริ่ม fetch_products()")  # DEBUG
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products"
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)

    try:
        # ✅ ใช้ requests.get() โดยตรง ไม่ต้องผ่าน requests.request()
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
        print(f"❌ ดึงข้อมูลสินค้าไม่สำเร็จ: {e}")
        return []
