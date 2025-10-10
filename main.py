from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import time

from api.shopee_api import shopee_get_item_list  # ฟังก์ชันดึงสินค้าของคุณ
from services.shopee_auth import get_shopee_refresh_access_token  # ฟังก์ชัน refresh token

# ===== Scheduler =====
scheduler = BackgroundScheduler(timezone="Asia/Bangkok")

# === job: refresh Shopee token ทุก 3.5 ชั่วโมง ===
def refresh_token_job():
    print(f"🔄 Running refresh_token_job at {datetime.now()}")
    data = get_shopee_refresh_access_token()
    if data:
        print("✅ Shopee token refreshed")
    else:
        print("❌ Failed to refresh token")

scheduler.add_job(refresh_token_job, 'interval', minute=15, id="refresh_shopee_token")

# === job: ดึงข้อมูลสินค้าจาก Shopee วันละครั้ง ===
def shopee_daily_job():
    print(f"📦 Running shopee_daily_job at {datetime.now()}")
    shopee_get_item_list()
    print("✅ Shopee items fetched")

scheduler.add_job(shopee_daily_job, 'cron', hour=2, minute=0, id="shopee_daily_fetch")
# cron hour=2 → ดึงตอนตี 2 ของทุกวัน ปรับเวลาได้ตามต้องการ

# เริ่ม scheduler
scheduler.start()
print("🟢 Scheduler started...")

# ทำให้ main thread ไม่ exit
try:
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print("🔴 Scheduler stopped")
