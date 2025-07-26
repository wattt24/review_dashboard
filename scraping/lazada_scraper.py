# import requests
# from bs4 import BeautifulSoup
# import time

# def scrape_lazada(keyword="เตาแก๊ส fujika", max_pages=2):
#     print(f"🔍 เริ่มดึงข้อมูลจาก Lazada ด้วย keyword: {keyword}")

#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     all_products = []

#     for page in range(1, max_pages + 1):
#         search_url = f"https://www.lazada.co.th/catalog/?q={keyword.replace(' ', '+')}&page={page}"
#         res = requests.get(search_url, headers=headers)
#         if res.status_code != 200:
#             print(f"❌ ไม่สามารถดึงหน้าที่ {page} ได้ (Status {res.status_code})")
#             continue

#         soup = BeautifulSoup(res.text, "html.parser")
#         items = soup.select("div[data-qa-locator='product-item']")

#         if not items:
#             print("⚠️ ไม่พบสินค้าในหน้านี้")
#             continue

#         for item in items:
#             name = item.select_one("div[data-qa-locator='product-item-name']")
#             price = item.select_one("span[data-qa-locator='product-item-price']")
#             rating = item.select_one("span.score")
#             review_count = item.select_one("span.review")

#             product_data = {
#                 "name": name.text.strip() if name else "N/A",
#                 "price": price.text.strip() if price else "N/A",
#                 "rating": rating.text.strip() if rating else "N/A",
#                 "reviews": review_count.text.strip() if review_count else "0"
#             }

#             print(f"📦 {product_data['name']} | 💰 {product_data['price']} | ⭐️ {product_data['rating']} | รีวิว: {product_data['reviews']}")
#             all_products.append(product_data)

#         time.sleep(1)  # หยุดนิดนึงกันโดน block

#     print(f"✅ ดึงข้อมูลจาก Lazada เสร็จสิ้น: {len(all_products)} รายการ")
#     return all_products
def scrape_lazada():
    print("เริ่มดึงข้อมูล lazada (mock)...")
    # mock data จำลองรีวิวสินค้า
    mock_reviews = [
        {"product_id": "1234", "review": "สินค้าดีมาก", "rating": 5, "author": "ลูกค้า A"},
        {"product_id": "5678", "review": "ส่งช้าไปนิด", "rating": 3, "author": "ลูกค้า B"},
    ]
    print(f"ดึงข้อมูล lazada mock เสร็จ: {len(mock_reviews)} รีวิว")
    return mock_reviews
