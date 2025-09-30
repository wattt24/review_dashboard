# services/facebook_auth.py
import requests
import streamlit as st
from datetime import datetime, timedelta
from utils.token_manager import save_token, get_latest_token, get_sheet
from utils.config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_PAGE_IDS  # import จาก config


sheet = get_sheet()
def get_all_page_tokens():
    """
    คืนค่า dict {page_id: access_token} สำหรับทุกเพจ (หลาย account)
    refresh token ด้วยฟังก์ชัน facebook_refresh_token() ถ้าหมดอายุ
    """
    page_ids = [pid.strip() for pid in FACEBOOK_PAGE_IDS.split(",") if pid.strip()]
    page_tokens = {}

    for page_id in page_ids:

        facebook_refresh_token(page_id)

        # ดึง token ล่าสุดจาก Google Sheet
        token_data = get_latest_token("facebook", page_id)
        if not token_data or not token_data.get("access_token"):
            print(f"⚠️ Facebook token สำหรับเพจ/ยูส {page_id} ไม่พร้อมใช้งาน")
            continue

        user_token = token_data["access_token"]

        # ดึง page token จริงจาก Facebook Graph API
        url = f"https://graph.facebook.com/v17.0/{page_id}"
        params = {"fields": "access_token", "access_token": user_token}
        resp = requests.get(url, params=params).json()

        if "access_token" in resp:
            page_tokens[page_id] = resp["access_token"]
            # บันทึกลง Google Sheet ใช้ platform=facebook, account_id=page_id
            save_token(
                platform="facebook",
                account_id=page_id,
                access_token=resp["access_token"],
                refresh_token="",
                expires_in=token_data.get("expires_in", 60*24*60*60),  # ใช้ค่าเดิมถ้ามี
            )
    return page_tokens

def validate_token(access_token):
    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
    }
    resp = requests.get(url, params=params).json()
    return resp

# services/facebook_auth.py
def facebook_refresh_token(page_id: str) -> dict | None:
    token_data = get_latest_token("facebook", page_id)
    if not token_data:
        print(f"❌ No token found for Facebook page {page_id}")
        return None

    try:
        url = "https://graph.facebook.com/v17.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": FACEBOOK_APP_ID,
            "client_secret": FACEBOOK_APP_SECRET,
            "fb_exchange_token": token_data["access_token"],
        }
        resp = requests.get(url, params=params).json()

        if "error" in resp:
            print(f"❌ Facebook refresh failed: {resp['error']}")
            return None

        if "access_token" not in resp:
            print(f"❌ No access_token in refresh response: {resp}")
            return None

        # ตรวจสอบ token validity
        debug_info = validate_token(resp["access_token"])
        if not debug_info.get("data", {}).get("is_valid"):
            print(f"⚠️ Refreshed token invalid for page {page_id}: {debug_info}")
            return None

        expires_in = resp.get("expires_in", 60 * 24 * 60 * 60)

        # บันทึกลง Google Sheet
        save_token(
            platform="facebook",
            account_id=page_id,
            access_token=resp["access_token"],
            refresh_token="",
            expires_in=expires_in,
        )

        print(f"✅ Facebook token refreshed and saved for page {page_id}")
        # ✅ ปรับ return ให้ชัดเจน
        return {
            "access_token": resp["access_token"],
            "expires_in": expires_in
        }

    except Exception as e:
        print(f"❌ Error refreshing Facebook token for page {page_id}: {e}")
        return None


