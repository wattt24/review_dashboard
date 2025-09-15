import requests
from utils.token_manager import save_token
import os
from datetime import datetime

def refresh_facebook_token(current_token, account_id):
    url = "https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": os.environ["FB_APP_ID"],
        "client_secret": os.environ["FB_APP_SECRET"],
        "fb_exchange_token": current_token
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "access_token" in data:
        # บันทึกลง Google Sheet
        save_token(
            platform="facebook",
            account_id=account_id,
            access_token=data["access_token"],
            refresh_token="",
            expires_in=data.get("expires_in", 0)
        )
        return data
    else:
        raise Exception(f"Facebook token refresh failed: {data}")
def get_page_token(user_access_token, page_id, account_id):
    url = f"https://graph.facebook.com/v17.0/{page_id}"
    params = {"fields": "access_token", "access_token": user_access_token}
    resp = requests.get(url, params=params).json()
    if "access_token" in resp:
        save_token(
            platform="facebook_page",
            account_id=account_id,
            access_token=resp["access_token"],
            refresh_token="",
            expires_in=60*24*60*60  # ปกติ page token ไม่มีวันหมดอายุแบบ short-lived
        )
        return resp["access_token"]
    else:
        raise Exception(f"Get Page Token failed: {resp}")
def validate_token(access_token):
    url = "https://graph.facebook.com/debug_token"
    params = {
        "input_token": access_token,
        "access_token": f"{os.environ['FB_APP_ID']}|{os.environ['FB_APP_SECRET']}"
    }
    resp = requests.get(url, params=params).json()
    return resp