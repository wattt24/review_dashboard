#main.py
from apscheduler.schedulers.blocking import BlockingScheduler
import time
from api.fujikathailand_rest_api import fetch_store_fujikathailand_reviews, fetch_comments_fujikathailand_reviews
import datetime
LAZADA_ACCOUNT_ID = "pirattapong.v@gmail.com"
from  services.shopee_auth import shopee_refresh_access_token  # import ฟังก์ชัน
from utils.config import SHOPEE_PARTNER_ID, SHOPEE_PARTNER_KEY, SHOPEE_SHOP_ID
from services.lazada_auth import lazada_refresh_access_token
# ====== ตั้งค่า Shopee ======
def refresh_token_job():
    print(f"🔄 Running Shopee token refresh job at {datetime.datetime.now()}")
    shopee_refresh_access_token(
        partner_id=SHOPEE_PARTNER_ID, partner_key=SHOPEE_PARTNER_KEY, shop_id=SHOPEE_SHOP_ID)
    
def refresh_lazada_token_job():
    print(f"🔄 [Lazada Refresh Job] {datetime.datetime.now()}")
    try:
        lazada_refresh_access_token(account_id=LAZADA_ACCOUNT_ID)
        print("✅ Lazada token refreshed successfully\n")
    except Exception as e:
        print(f"❌ Lazada refresh failed: {e}\n")

def fetch_review_job():
    print(f"🕓 [Review Fetch] เริ่มดึงรีวิวที่ {datetime.datetime.now()}")
    try:
        fetch_store_fujikathailand_reviews()
        fetch_comments_fujikathailand_reviews()
        print("✅ ดึงรีวิวสำเร็จ\n")
    except Exception as e:
        print(f"❌ ดึงรีวิวล้มเหลว: {e}\n")


if __name__ == "__main__":

    scheduler = BlockingScheduler()
    #1️ รีฟรีช
    # ตั้ง interval 3 ชั่วโมง = 3.5*3600 = 12600 วินาที
    scheduler.add_job(refresh_token_job, 'interval', seconds=12600, id=SHOPEE_SHOP_ID)
    print("⏰ Scheduler started, refreshing every 12600 วินาที ")

    # Lazada: ทุก 20 วัน (20 * 24 * 60 * 60 = 1,728,000 วินาที)
    scheduler.add_job(refresh_lazada_token_job, "interval", days=20, id="lazada_refresh")


    # 2️ รีวิว: ดึงข้อมูลทุกวันตอนตี 3
    scheduler.add_job(fetch_review_job, 'cron', hour=3, minute=0, id='Fujikathailand')

    print("  - ดึงรีวิว WordPress/WooCommerce ทุกวันเวลา 03:00")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Scheduler stopped.")

    scheduler.start()
