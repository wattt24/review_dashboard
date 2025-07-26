# # scraping/line_oa_scraper.py

# def scrape_line_oa():
#     print("📱 [LINE OA] เริ่มดึงข้อมูลข้อความ/รีวิวจาก LINE Official Account...")

#     # TODO: ใส่โค้ดเชื่อม LINE Messaging API หรือ scraping จริง ๆ ที่นี่
#     # เวอร์ชัน mockup:
#     messages = [
#         {"user": "ลูกค้า C", "message": "สินค้าดี บริการเยี่ยม", "timestamp": "2025-07-18 10:00"},
#         {"user": "ลูกค้า D", "message": "ตอบเร็วมาก ประทับใจ", "timestamp": "2025-07-18 11:00"},
#     ]

#     for msg in messages:
#         print(f"{msg['user']} → 💬 {msg['message']} 🕒 {msg['timestamp']}")

#     print("✅ [LINE OA] ดึงข้อมูลสำเร็จ")
#     return messages


# if __name__ == "__main__":
#     scrape_line_oa()
def scrape_line_oa():
    print("เริ่มดึงข้อมูล line (mock)...")
    # mock data จำลองรีวิวสินค้า
    mock_reviews = [
        {"product_id": "1234", "review": "สินค้าดีมาก", "rating": 5, "author": "ลูกค้า A"},
        {"product_id": "5678", "review": "ส่งช้าไปนิด", "rating": 3, "author": "ลูกค้า B"},
    ]
    print(f"ดึงข้อมูล line mock เสร็จ: {len(mock_reviews)} รีวิว")
    return mock_reviews
