# เอาไว้เก็บลง Google Sheet เป็นศูนย์กลาง token ของทุกแพลตฟอร์ม (Shopee, Lazada, Facebook ฯลฯ) 
# utils/token_manager.py
import os
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials 
import streamlit as st


# Facebook ใช้ long-lived token แทน refresh_token
# สามารถเพิ่ม API สำหรับ refresh ได้ถ้าจำเป็น

# ===== Google Sheet Setup =====
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client():
    key_path = os.getenv("SERVICE_ACCOUNT_JSON") or "/etc/secrets/SERVICE_ACCOUNT_JSON"
    creds = None

    if os.path.exists(key_path):
        creds = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
    else:
        try:
            service_account_info = st.secrets["SERVICE_ACCOUNT_JSON"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(service_account_info), scope)
        except Exception as e:
            raise FileNotFoundError(f"❌ ไม่พบ Service Account JSON") from e

    return gspread.authorize(creds)

client = get_gspread_client()
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"] or st.secrets["GOOGLE_SHEET_ID"]).sheet1

# ===== Token Manager =====
def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
    
    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat() if refresh_expires_in else ""
    
    try:
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):
            if record["platform"] == platform and str(record["account_id"]) == int(account_id):
                sheet.update(f"A{idx}:G{idx}", [[
                    platform, account_id, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
                ]])
                return

        # ถ้าไม่เจอ row เดิม → เพิ่มใหม่
        sheet.append_row([
            platform, account_id, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
        ])

    except Exception as e:
        print("❌ save_token error:", str(e))


def get_latest_token(platform, account_id):
    try:
        records = sheet.get_all_records()
        account_id_str = str(account_id).strip()
        for idx, record in enumerate(records, start=2):
            if str(record.get("platform", "")).strip().lower() == str(platform).strip().lower() \
               and str(record.get("account_id", "")).strip() == account_id_str:
                return {
                    "access_token": record.get("access_token", ""),
                    "refresh_token": record.get("refresh_token", ""),
                    "expired_at": record.get("expired_at"),
                    "refresh_expired_at": record.get("refresh_expired_at")
                }
    except Exception as e:
        print("❌ get_latest_token error:", str(e))
    return None


# ===== Auto-refresh token =====
def auto_refresh_token(platform, account_id):
    print(f"[{datetime.now().isoformat()}] ⚡ Checking token for {platform}:{account_id}")
    token_data = get_latest_token(platform, account_id)
    if not token_data:
        print(f"❌ No token found for {platform}:{account_id}")
        return None

    expired_at = token_data.get("expired_at")
    expired = True
    if expired_at:
        expired_at_dt = datetime.fromisoformat(expired_at)
        expired = expired_at_dt <= datetime.now()

    if not expired:
        return token_data["access_token"]

    # หมดอายุ → refresh
    try:
        if platform == "shopee":
            from services.shopee_auth import refresh_token as shopee_refresh_token
            new_data = shopee_refresh_token(token_data["refresh_token"], account_id)
            save_token(platform, account_id,
                       new_data["access_token"],
                       new_data["refresh_token"],
                       new_data.get("expire_in", 0),
                       new_data.get("refresh_expires_in", 0))
            print(f"[{datetime.now().isoformat()}] ✅ Shopee token refreshed")
            return new_data["access_token"]

        elif platform == "lazada":
            from services.lazada_auth import lazada_refresh_token as lazada_refresh_token
            new_data = lazada_refresh_token(token_data["refresh_token"], account_id)
            save_token(platform, account_id,
                       new_data["access_token"],
                       new_data["refresh_token"],
                       new_data.get("expires_in", 0),
                       new_data.get("refresh_expires_in", 0))
            print(f"[{datetime.now().isoformat()}] ✅ Lazada token refreshed")
            return new_data["access_token"]

        elif platform in ["facebook", "facebook"]:
            from services.facebook_auth import refresh_facebook_token
            new_data = refresh_facebook_token(token_data["access_token"], account_id)

            if "access_token" in new_data:
                # สำหรับ Facebook Page หลาย account ใช้ token เดียวกัน → update ทุก row
                records = sheet.get_all_records()
                for idx, record in enumerate(records, start=2):
                    if record["platform"] == platform and record["access_token"] == token_data["access_token"]:
                        sheet.update(f"C{idx}", new_data["access_token"])
                        if "expires_in" in new_data:
                            expired_at = (datetime.now() + timedelta(seconds=new_data["expires_in"])).isoformat()
                            sheet.update(f"E{idx}", expired_at)
                        sheet.update(f"G{idx}", datetime.now().isoformat())
                print(f"Updating token for {platform}:{account_id} at row {idx}")
                print(f"[{datetime.now().isoformat()}] ✅ Facebook token refreshed for all related accounts")
                return new_data["access_token"]


        else:
            print(f"❌ Auto-refresh not implemented for {platform}")
            return token_data["access_token"]

    except Exception as e:
        print(f"❌ Auto-refresh failed for {platform}:{account_id} - {str(e)}")
        return None

