
# scraping/fujikaservice_scraper.py
# fujika_service_api.py
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from utils.config import FUJIKA_SERVICE_SITE_URL, FUJIKA_SERVICE_CONSUMER_KEY, FUJIKA_SERVICE_CONSUMER_SECRET

def fetch_all_products_fujikaservice(per_page=100):
    """
    ดึงข้อมูล Products จาก WooCommerce
    คืนค่าเป็น DataFrame
    """
    all_products = []
    page = 1
    while True:
        try:
            resp = requests.get(
                f"{FUJIKA_SERVICE_SITE_URL}/wp-json/wc/v3/products",
                auth=HTTPBasicAuth(FUJIKA_SERVICE_CONSUMER_KEY, FUJIKA_SERVICE_CONSUMER_SECRET),
                params={"per_page": per_page, "page": page},
                timeout=10
            )
            resp.raise_for_status()
            products = resp.json()
            if not products:
                break
            all_products.extend(products)
            page += 1
        except requests.RequestException as e:
            print(f"❌ Error fetching products: {e}")
            break

    # แปลงเป็น DataFrame
    df_products = pd.DataFrame([
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "price": float(p.get("price") or 0),
            "stock_quantity": p.get("stock_quantity", 0),
            "average_rating": float(p.get("average_rating") or 0),
            "rating_count": p.get("rating_count", 0)
        }
        for p in all_products
    ])
    return df_products
