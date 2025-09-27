from apscheduler.schedulers.background import BackgroundScheduler
import time
from services.facebook_auth import refresh_facebook_token

# Shopee ทุก 3 ชั่วโมง 40 นาที
scheduler.add_job(refresh_shopee, 'interval', hours=3, minutes=40)

# Lazada ทุก 4 ชั่วโมง
scheduler.add_job(refresh_lazada, 'interval', hours=4)

# Facebook ทุก 1 ชั่วโมง 20 นาที (token ใช้กับ 2 เพจได้เลย)
scheduler.add_job(refresh_facebook_token, 'interval', hours=1, minutes=20)

scheduler.start()

print("🚀 Scheduler started")
try:
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
