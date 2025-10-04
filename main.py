# main.py
# เรียกใช้แบบตรงๆ เพื่อควบคุมรอบของเวลา refresh ของแต่ละ platform แยกกัน
from apscheduler.schedulers.background import BackgroundScheduler
from services.shopee_auth import shopee_refresh_token
# from services.lazada_auth import lazada_refresh_token
scheduler = BackgroundScheduler()
from utils.config import SHOPEE_SHOP_ID
def safe_job(func, *args):
    try:
        func(*args)
    except Exception as e:
        print(f"❌ Error running job {func.__name__}: {e}")
# Shopee → ทุก 1 ชั่วโมง 15 นาที
scheduler.add_job(safe_job, shopee_refresh_token, "interval", hours=1, minutes=15, args=[SHOPEE_SHOP_ID])

# Lazada → ทุก 4 ชั่วโมง
# scheduler.add_job(safe_job,lazada_refresh_token, "interval", hours=4, args=["REFRESH_TOKEN", "STORE_A"])

scheduler.start()

try:
    import time
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
