# main.py
# เรียกใช้แบบตรงๆ เพื่อควบคุมรอบของเวลา refresh ของแต่ละ platform แยกกัน
from apscheduler.schedulers.background import BackgroundScheduler
from services.shopee_auth import shopee_refresh_token
from services.lazada_auth import lazada_refresh_token
from services.facebook_auth import facebook_refresh_token
scheduler = BackgroundScheduler()

# Shopee → ทุก 3 ชั่วโมง
scheduler.add_job(shopee_refresh_token, "interval", hours=3, args=["SHOP_ID_1"])

# Lazada → ทุก 4 ชั่วโมง
scheduler.add_job(lazada_refresh_token, "interval", hours=4, args=["REFRESH_TOKEN", "STORE_A"])

# Facebook → Page 1 ทุก 1 ชั่วโมง
scheduler.add_job(facebook_refresh_token, "interval", hours=1, args=["PAGE_ID_1"])

# Facebook → Page 2 ทุก 2 ชั่วโมง
scheduler.add_job(facebook_refresh_token, "interval", hours=2, args=["PAGE_ID_2"])

scheduler.start()

try:
    import time
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
