# # scraping/cps_oem_scraper.py

# def scrape_cps_oem():
#     print("🔍 [CPS_OEM] เริ่มดึงข้อมูลจากเว็บไซต์ OEM...")
    
#     # TODO: ใส่โค้ดจริงสำหรับ scraping หรือ API ที่นี่
#     # เวอร์ชัน mockup:
#     data = [
#         {"model": "OEM-1234", "status": "Available", "price": 1200},
#         {"model": "OEM-5678", "status": "Out of stock", "price": 1500},
#     ]

#     for item in data:
#         print(f"Model: {item['model']} | Status: {item['status']} | Price: {item['price']}")

#     print("✅ [CPS_OEM] ดึงข้อมูลสำเร็จ")
#     return data


# if __name__ == "__main__":
#     scrape_cps_oem()
def scrape_cps_oem():
    print("เริ่มดึงข้อมูล cps (mock)...")
    # mock data จำลองรีวิวสินค้า
    mock_reviews = [
        {"product_id": "1234", "review": "สินค้าดีมาก", "rating": 5, "author": "ลูกค้า A"},
        {"product_id": "5678", "review": "ส่งช้าไปนิด", "rating": 3, "author": "ลูกค้า B"},
    ]
    print(f"ดึงข้อมูล cps mock เสร็จ: {len(mock_reviews)} รีวิว")
    return mock_reviews
