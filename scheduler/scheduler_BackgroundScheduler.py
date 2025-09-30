from apscheduler.schedulers.background import BackgroundScheduler
from services.facebook_auth import get_all_page_tokens, facebook_refresh_token
from services.shopee_auth import shopee_refresh_token, get_latest_token as get_shopee_token
from utils.lazada_auth import lazada_refresh_token
from utils.token_manager import get_latest_token
from utils.config import SHOPEE_SHOP_ID, FACEBOOK_PAGE_IDS, LAZADA_STORE_IDS  # ใส่ store_id, page_ids

import time

def refresh_all_tokens():
    print("🔄 Starting token refresh job...")

    # --- Facebook ---
    page_ids = [pid.strip() for pid in FACEBOOK_PAGE_IDS.split(",") if pid.strip()]
    for page_id in page_ids:
        facebook_refresh_token(page_id)

    # --- Shopee ---
    for shop_id in SHOPEE_SHOP_ID.split(","):
        shop_id = shop_id.strip()
        token_data = get_shopee_token("shopee", shop_id)
        if token_data:
            shopee_refresh_token(shop_id)

    # --- Lazada ---
    for store_id in LAZADA_STORE_IDS.split(","):
        store_id = store_id.strip()
        token_data = get_latest_token("lazada", store_id)
        if token_data:
            lazada_refresh_token(token_data["refresh_token"], store_id)

    print("✅ Token refresh job completed.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # ตั้งเวลา refresh ทุก 6 ชั่วโมง (ปรับได้)
    scheduler.add_job(refresh_all_tokens, 'interval', hours=6, id='refresh_tokens')
    scheduler.start()
    print("🟢 Background scheduler started. Refresh tokens every 6 hours.")

    try:
        # keep the script running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("🛑 Scheduler stopped.")
