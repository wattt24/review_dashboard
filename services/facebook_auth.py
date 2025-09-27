# services/facebook_auth.py
import requests
import streamlit as st
from datetime import datetime
from utils.token_manager import auto_refresh_token, save_token
from utils.config import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, FACEBOOK_PAGE_IDS  # import จาก config



def get_all_page_tokens():
    """
    คืนค่า dict {page_id: access_token} สำหรับทุกเพจ (หลาย account)
    auto-refresh token ถ้าหมดอายุ
    """
    page_ids = [pid.strip() for pid in FACEBOOK_PAGE_IDS.split(",") if pid.strip()]
    page_tokens = {}
    
    for page_id in page_ids:
        # ดึง token ของ user/account
        user_token = auto_refresh_token("facebook", account_id=page_id)
        if not user_token:
            print(f"⚠️ Facebook token สำหรับเพจ/ยูส {page_id} ไม่พร้อมใช้งาน")
            continue
        
        # ดึง page token ถ้าเป็นเพจ
        url = f"https://graph.facebook.com/v17.0/{page_id}"
        params = {"fields": "access_token", "access_token": user_token}
        resp = requests.get(url, params=params).json()
        if "access_token" in resp:
            page_tokens[page_id] = resp["access_token"]
            # บันทึกลง Google Sheet
            save_token("facebook_page", page_id, resp["access_token"], "", expires_in=60*24*60*60)
        else:
            print(f"❌ ไม่สามารถดึง token ของเพจ {page_id}: {resp}")
    
    return page_tokens

def validate_token(access_token):
    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
    }
    resp = requests.get(url, params=params).json()
    return resp
def refresh_facebook_token(current_token, account_id):
    url = "https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": FACEBOOK_APP_ID,
        "client_secret": FACEBOOK_APP_SECRET,
        "fb_exchange_token": current_token
    }

    resp = requests.get(url, params=params)
    data = resp.json()

    if "access_token" in data:
        return data  # ✅ คืนค่าเฉย ๆ ไม่บันทึก
    else:
        raise Exception(f"Facebook token refresh failed: {data}")