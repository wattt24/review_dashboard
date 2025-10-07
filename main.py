# เรียกใช้แบบตรงๆ เพื่อควบคุมรอบของเวลา refresh ของแต่ละ platform แยกกัน
# main.py
from apscheduler.schedulers.background import BackgroundScheduler
from api.fujikathailand_rest_api import fetch_store_wc_reviews, fetch_comments_reviews
from services.shopee_auth import shopee_refresh_token
from utils.config import SHOPEE_SHOP_ID

scheduler = BackgroundScheduler()

def safe_job(func, *args):
    try:
        func(*args)
    except Exception as e:
        print(f"❌ Error running job {func.__name__}: {e}")

# Shopee → ทุก 1 ชั่วโมง 15 นาที
scheduler.add_job(
    func=safe_job,            # ฟังก์ชันที่จะรัน
    trigger="interval",       # กำหนด trigger เป็น keyword argument
    minutes=10,
    args=[shopee_refresh_token, SHOPEE_SHOP_ID]  # ส่ง func และ args ไปยัง safe_job
)
scheduler.add_job(
    func=safe_job, trigger="interval", hours=4, args=[fetch_store_wc_reviews])
scheduler.add_job(
    func=safe_job, trigger="interval", hours=4, args=[fetch_comments_reviews])
# scheduler.add_job(
#     func=safe_job,            # ฟังก์ชันที่จะรัน
#     trigger="interval",       # กำหนด trigger เป็น keyword argument
#     hours=1,
#     minutes=15,
#     args=[shopee_refresh_token, SHOPEE_SHOP_ID]  # ส่ง func และ args ไปยัง safe_job
# )

# Lazada → ทุก 4 ชั่วโมง
# scheduler.add_job(
#     func=safe_job,
#     trigger="interval",
#     hours=4,
#     args=[fetch_store_wc_reviews"]
# )

scheduler.start()

try:
    import time
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()


