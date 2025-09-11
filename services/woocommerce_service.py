# services/woocommerce_service.py
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

# โหลด .env
load_dotenv()

WOOCOMMERCE_URL = os.getenv("WOOCOMMERCE_URL")
WOOCOMMERCE_CONSUMER_KEY = os.getenv("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.getenv("WOOCOMMERCE_CONSUMER_SECRET")

# ----------------- ดึงสินค้าทั้งหมด -----------------
def fetch_all_product_sales(per_page=100, timeout=15, max_pages=50, order_status="completed"):
    print("✅ เริ่ม fetch_products_with_sales()")
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)

    # ----------------- ดึงข้อมูลสินค้า -----------------
    products_url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products"
    all_products = []
    page = 1
    while True:
        resp = requests.get(
            products_url,
            auth=auth,
            params={"per_page": per_page, "page": page},
            timeout=timeout
        )
        resp.raise_for_status()
        products = resp.json()
        if not products:
            break

        for p in products:
            image_url = p.get("images", [{}])[0].get("src", "")
            all_products.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "price": float(p.get("price") or 0),
                "image_url": image_url,
                "stock_quantity": p.get("stock_quantity", 0),
                "average_rating": float(p.get("average_rating", "0") or 0),
                "rating_count": p.get("rating_count", 0),
                "quantity_sold": 0,
                "total_revenue": 0.0
            })

        if len(products) < per_page or page >= max_pages:
            break
        page += 1

    # ----------------- ดึงยอดขาย -----------------
    orders_url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"
    sales_data = {}
    page = 1
    while True:
        resp = requests.get(
            orders_url,
            auth=auth,
            params={"per_page": per_page, "page": page, "status": order_status},
            timeout=timeout
        )
        resp.raise_for_status()
        orders = resp.json()
        if not orders:
            break

        for order in orders:
            for item in order.get("line_items", []):
                product_name = item.get("name")
                qty = item.get("quantity", 0)
                total = float(item.get("total", 0.0))
                if product_name not in sales_data:
                    sales_data[product_name] = {"quantity": 0, "revenue": 0.0}
                sales_data[product_name]["quantity"] += qty
                sales_data[product_name]["revenue"] += total

        if len(orders) < per_page or page >= max_pages:
            break
        page += 1

    # ----------------- รวมข้อมูลสินค้า + ยอดขาย -----------------
    for product in all_products:
        if product["name"] in sales_data:
            product["quantity_sold"] = sales_data[product["name"]]["quantity"]
            product["total_revenue"] = round(sales_data[product["name"]]["revenue"], 2)

    print(f"✅ รวมข้อมูลสำเร็จ: {len(all_products)} รายการ")
    return all_products
