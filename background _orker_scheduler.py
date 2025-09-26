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
from utils.token_manager import get_all_tokens, save_token
from services.shopee_api import refresh_shopee_token

def refresh_all():
    records = get_all_tokens("Tokens")
    for row in records:
        platform = row["platform"].lower()
        account_id = row["account_id"]
        refresh_token = row["refresh_token"]

        if platform == "shopee":
            result = refresh_shopee_token(account_id, refresh_token)
            if "access_token" in result:
                save_token("shopee", account_id,
                           result["access_token"],
                           result["refresh_token"],
                           result.get("expire_in"),
                           30*24*3600)

if __name__ == "__main__":
    refresh_all()