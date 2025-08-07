
# scraping/fujikaservice_scraper.py
import requests
from utils.config import FUJIKA_SERVICE_API_KEY

def fetch_service_feedback():
    url = "https://fujikaservice.com/api/v1/feedback"
    headers = {"Authorization": f"Bearer {FUJIKA_SERVICE_API_KEY}"}
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []
# scraping/fujikaservice_scraper.py

def fetch_service_data():
    # TODO: เขียน logic ดึงข้อมูลจากระบบบริการหลังการขายของ fujikaservice.com
    # เช่น web scraping หรือ REST API ถ้ามี
    print("✅ เรียกใช้งาน fetch_service_data สำเร็จจ้าาาา")
    return [
        {"ticket_id": 1, "status": "open", "subject": "แจ้งซ่อมสินค้า"},
        {"ticket_id": 2, "status": "closed", "subject": "ขอใบรับประกัน"},
    ]
