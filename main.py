from apscheduler.schedulers.background import BackgroundScheduler
import time

def refresh_facebook():
    print("🔄 Refresh Facebook Token")

def refresh_shopee():
    print("🔄 Refresh Shopee Token")

def refresh_lazada():
    print("🔄 Refresh Lazada Token")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()

    # Facebook: ทุกๆ 30 วัน (เผื่อก่อนหมดอายุจริง)
    scheduler.add_job(refresh_facebook, "interval", days=30)

    # Shopee: ทุกๆ 3 ชั่วโมง
    scheduler.add_job(refresh_shopee, "interval", hours=3)

    # Lazada: ทุกๆ 30 นาที
    scheduler.add_job(refresh_lazada, "interval", minutes=30)

    scheduler.start()

    print("✅ Token refresher started")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
