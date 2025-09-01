# scraping/fujikathailand_scraper.py

import requests
from utils.province_mapping import province_code_map
from requests.auth import HTTPBasicAuth
from utils.config import WOOCOMMERCE_URL, WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET,FUJIKA_WP_USER,FUJIKA_WP_PASSWORD,FUJIKA_WP_APP_PASSWORD_API_ACCESS
from collections import defaultdict

# -------------------- ฟังก์ชันช่วยแปลงจังหวัดเป็นภูมิภาค --------------------
def province_to_region(province):
    province = province.strip()
    
    north = ["Chiang Mai","Chiang Rai","Nan","Phrae","Lampang","Lamphun","Mae Hong Son","Phayao","Uttaradit",
             "Sukhothai","Phitsanulok","Phichit","Kamphaeng Phet","Phetchabun","Tak","Nakhon Sawan","Uthai Thani"]
    
    northeast = ["Khon Kaen","Kalasin","Nong Khai","Nakhon Phanom","Sakon Nakhon","Udon Thani","Nong Bua Lam Phu",
                 "Loei","Mukdahan","Amnat Charoen","Yasothon","Chaiyaphum","Maha Sarakham","Roi Et",
                 "Nakhon Ratchasima","Buri Ram","Surin","Si Sa Ket","Ubon Ratchathani","Bueng Kan"]
    
    central = ["Bangkok","Phra Nakhon Si Ayutthaya","Ang Thong","Chai Nat","Lop Buri","Sing Buri","Saraburi",
               "Nonthaburi","Pathum Thani","Samut Prakan","Samut Sakhon","Samut Songkhram","Nakhon Pathom",
               "Nakhon Nayok","Suphan Buri"]
    
    west = ["Kanchanaburi","Ratchaburi","Phetchaburi","Prachuap Khiri Khan","Tak"]
    
    east = ["Chon Buri","Sa Kaeo","Prachin Buri","Chachoengsao","Rayong","Trat","Chanthaburi"]
    south = ["Krabi","Chumphon","Ranong","Surat Thani","Trang","Nakhon Si Thammarat","Narathiwat","Pattani",
             "Phangnga","Phatthalung","Phuket","Songkhla","Satun","Yala"]

    if province in north:
        return "ภาคเหนือ"
    elif province in northeast:
        return "ภาคตะวันออกเฉียงเหนือ"
    elif province in central:
        return "ภาคกลาง"
    elif province in west:
        return "ภาคตะวันตก"
    elif province in east:
        return "ภาคตะวันออก"
    elif province in south:
        return "ภาคใต้"
    else:
        return "ไม่พบจังหวัด"

# -------------------- ดึงข้อมูลสินค้า --------------------
def fetch_all_products(per_page=100, timeout=15, max_pages=50):
    """ดึงข้อมูลสินค้าทั้งหมด"""
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products"
    all_products = []
    page = 1

    while True:
        resp = requests.get(url, auth=auth, params={"per_page": per_page, "page": page}, timeout=timeout)
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

    return all_products

# -------------------- ดึงยอดขายและผู้ซื้อ --------------------
def fetch_sales_and_buyers_all(order_status="completed", per_page=100, timeout=15, max_pages=50):
    
    auth = HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/orders"

    sales_data = {}
    buyers_list = []
    total_orders = 0
    page = 1

    while True:
        resp = requests.get(
            url,
            auth=auth,
            params={"per_page": per_page, "page": page, "status": order_status},
            timeout=timeout
        )
        resp.raise_for_status()
        orders = resp.json()
        if not orders:
            break

        for order in orders:
            total_orders += 1  # นับออเดอร์ทั้งหมด

            # ===== เก็บยอดขายต่อสินค้า =====
            for item in order.get("line_items", []):
                name = item.get("name")
                qty = item.get("quantity", 0)
                total = float(item.get("total", 0.0))
                if name not in sales_data:
                    sales_data[name] = {"quantity": 0, "revenue": 0.0}
                sales_data[name]["quantity"] += qty
                sales_data[name]["revenue"] += total

            # ===== เก็บข้อมูลผู้ซื้อ =====
            billing = order.get("billing", {})
            province_code = billing.get("state", "").strip().upper()
            province_name = province_code_map.get(province_code, province_code)

            buyers_list.append({
                "name": f"{billing.get('first_name','')} {billing.get('last_name','')}".strip(),
                "email": billing.get("email", "").strip().lower(),
                "phone": billing.get("phone", ""),
                "province": province_name,
                "region": province_to_region(province_name),
                "quantity": sum(i.get("quantity", 0) for i in order.get("line_items", []))  # เก็บจำนวนสินค้าทั้งออเดอร์
            })

        if len(orders) < per_page or page >= max_pages:
            break
        page += 1

    return sales_data, buyers_list, total_orders


# -------------------- รวมสินค้า + ยอดขาย + ผู้ซื้อ --------------------
# ดึงข้อมูลสินค้าพร้อมยอดขายและรายชื่อผู้ซื้อ
  
def fetch_all_product_sales():
    products = fetch_all_products()
    sales_data, buyers_list, total_orders = fetch_sales_and_buyers_all()

    # รวมยอดขายเข้ากับสินค้า
    for product in products:
        if product["name"] in sales_data:
            product["quantity_sold"] = sales_data[product["name"]]["quantity"]
            product["total_revenue"] = round(sales_data[product["name"]]["revenue"], 2)

    print(f"✅ ดึงข้อมูลสำเร็จ: {len(products)} สินค้า, {len(buyers_list)} ผู้ซื้อ, {total_orders} ออเดอร์")
    return products, buyers_list, total_orders

def summarize_buyers_with_quantity(buyers_list):
    buyer_data = defaultdict(lambda: {"purchase_count": 0, "total_quantity": 0})
    for b in buyers_list:
        email = b["email"]
        quantity = b.get("quantity", 1)  # จำนวนสินค้าที่ซื้อใน order
        buyer_data[email]["purchase_count"] += 1
        buyer_data[email]["total_quantity"] += quantity
        for key in ["name", "phone", "province", "region"]:
            if key not in buyer_data[email]:
                buyer_data[email][key] = b.get(key)
    return buyer_data


# post
# -------------------- ดึงโพสต์ --------------------
def fetch_posts(per_page=10):
    """
    ดึงโพสต์จาก WordPress REST API
    ต้องใช้ WordPress User + Application Password
    """
    url = f"{WOOCOMMERCE_URL}/wp-json/wp/v2/posts"
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS),
        params={"per_page": per_page}
    )
    resp.raise_for_status()
    return resp.json()

# -------------------- ดึงคอมเมนต์ --------------------
def fetch_comments(post_id):
    """
    ดึงคอมเมนต์ของโพสต์
    ต้องใช้ WordPress User + Application Password
    """
    url = f"{WOOCOMMERCE_URL}/wp-json/wp/v2/comments"
    resp = requests.get(
        url,
        auth=HTTPBasicAuth(FUJIKA_WP_USER, FUJIKA_WP_APP_PASSWORD_API_ACCESS),
        params={"post": post_id}
    )
    resp.raise_for_status()
    return resp.json()
# ดึงรีวิวจากสินค้า
def fetch_product_reviews(product_id=None, per_page=10):
    """
    ดึงรีวิวสินค้า (รวมเรทติ้ง)
    ถ้า product_id=None จะดึงรีวิวทั้งหมด
    """
    url = f"{WOOCOMMERCE_URL}/wp-json/wc/v3/products/reviews"
    params = {"per_page": per_page}
    if product_id:
        params["product"] = product_id

    resp = requests.get(url, auth=HTTPBasicAuth(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET), params=params)
    resp.raise_for_status()
    return resp.json()
def normalize_df_for_streamlit(df):
    """
    แปลงทุก column type object ที่เป็น list/dict ให้เป็น string
    เพื่อป้องกัน pyarrow ArrowInvalid
    """
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else "")
    return df
