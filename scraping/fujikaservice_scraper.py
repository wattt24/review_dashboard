# # scraping/fujikaservice_scraper.py

# import requests
# from bs4 import BeautifulSoup

# def scrape_fujikaservice():
#     print("🔧 [Fujikaservice] เริ่มดึงข้อมูลจาก fujikaservice.com...")

#     url = "https://fujikaservice.com/"  # เปลี่ยน URL ให้ตรงกับหน้าที่ต้องการ
#     headers = {
#         "User-Agent": "Mozilla/5.0"
#     }

#     try:
#         res = requests.get(url, headers=headers)
#         if res.status_code != 200:
#             print(f"❌ ไม่สามารถเข้าถึงเว็บไซต์ (Status {res.status_code})")
#             return

#         soup = BeautifulSoup(res.text, "html.parser")

#         # 🔍 ตัวอย่าง: ดึงชื่อสินค้าและรายละเอียดบริการ
#         services = soup.select(".service-title")  # ปรับ selector ตามโครง HTML จริง

#         for s in services:
#             print(f"🛠️ บริการ: {s.text.strip()}")

#         print("✅ [Fujikaservice] ดึงข้อมูลสำเร็จ")

#     except Exception as e:
#         print(f"⚠️ เกิดข้อผิดพลาด: {e}")
def scrape_fujikaservice():
    print("เริ่มดึงข้อมูล fujikaservice (mock)...")
    # mock data จำลองรีวิวสินค้า
    mock_reviews = [
        {"product_id": "1234", "review": "สินค้าดีมาก", "rating": 5, "author": "ลูกค้า A"},
        {"product_id": "5678", "review": "ส่งช้าไปนิด", "rating": 3, "author": "ลูกค้า B"},
    ]
    print(f"ดึงข้อมูล fujikaservice mock เสร็จ: {len(mock_reviews)} รีวิว")
    return mock_reviews
