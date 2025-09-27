from apscheduler.schedulers.background import BackgroundScheduler
from utils.token_manager import auto_refresh_token

scheduler = BackgroundScheduler()
# Shopee ทุก 3 ชั่วโมง 40 นาที
scheduler.add_job(lambda: auto_refresh_token("shopee", "54804"), 'interval', hours=3, minutes=40)
# Facebook ทุก 1 ชั่วโมง 20 นาที
scheduler.add_job(lambda: auto_refresh_token("facebook", "PAGE_ID_1"), 'interval', hours=1, minutes=20)

scheduler.start()

try:
    import time
    while True:
        time.sleep(60)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
    print('Scheduler shutdown.')