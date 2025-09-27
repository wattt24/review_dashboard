from apscheduler.schedulers.background import BackgroundScheduler
import time

def job1():
    print("✅ Refresh Shopee token...")

def job2():
    print("✅ Refresh Facebook token...")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(job1, 'interval', hours=3, minutes=40)
    scheduler.add_job(job2, 'interval', hours=1, minutes=20)
    scheduler.start()

    print("🚀 Scheduler started on Railway")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
