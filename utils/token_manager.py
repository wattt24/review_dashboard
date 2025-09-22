# เอาไว้เก็บลง Google Sheet เป็นศูนย์กลาง token ของทุกแพลตฟอร์ม (Shopee, Lazada, Facebook ฯลฯ) 
# utils/token_manager.py
import os , json
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
    """
    ใช้ Service Account JSON จาก Environment variable (Render) หรือ st.secrets (Streamlit Cloud)
    """
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")

    if service_account_json:
        # Render / env var เป็น string JSON
        service_account_info = json.loads(service_account_json)
    else:
        # Streamlit Cloud / st.secrets เป็น dict
        service_account_info = dict(st.secrets["SERVICE_ACCOUNT_JSON"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    return gspread.authorize(creds)

# ===== Load Google Sheet =====
client = get_gspread_client()
GOOGLE_SHEET = os.environ.get("GOOGLE_SHEET_ID") or st.secrets["GOOGLE_SHEET_ID"]

if not GOOGLE_SHEET:
    raise ValueError("❌ ไม่พบ GOOGLE_SHEET_ID ใน os.environ")

sheet = client.open_by_key(GOOGLE_SHEET).sheet1

def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
    now = datetime.now()

    # Access Token expiry
    expired_at = (now + timedelta(seconds=expires_in)).isoformat() if expires_in else ""

    # Refresh Token expiry
    refresh_expired_at = ""
    if platform.lower() == "shopee":
        # Shopee refresh token มีอายุ 30 วัน → คำนวณเอง
        refresh_expired_at = (now + timedelta(days=30)).isoformat()
    elif refresh_expires_in:  
        # Lazada หรือ platform อื่นที่ส่งค่ามา
        refresh_expired_at = (now + timedelta(seconds=refresh_expires_in)).isoformat()

    account_id_str = str(account_id).strip()
    
    try:
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):
            if str(record.get("platform", "")).strip().lower() == str(platform).strip().lower() \
               and str(record.get("account_id", "")).strip() == account_id_str:
                sheet.update(f"A{idx}:G{idx}", [[
                    platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, now.isoformat()
                ]])
                return

        # ถ้าไม่เจอ row เดิม → เพิ่มใหม่
        sheet.append_row([
            platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, now.isoformat()
        ])

    except Exception as e:
        print("❌ save_token error:", str(e))
# def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
#     expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
#     refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat() if refresh_expires_in else ""
    
#     account_id_str = str(account_id).strip()
    
#     try:
#         records = sheet.get_all_records()
#         for idx, record in enumerate(records, start=2):
#             if str(record.get("platform", "")).strip().lower() == str(platform).strip().lower() \
#                and str(record.get("account_id", "")).strip() == account_id_str:
#                 sheet.update(f"A{idx}:G{idx}", [[
#                     platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
#                 ]])
#                 return

#         # ถ้าไม่เจอ row เดิม → เพิ่มใหม่
#         sheet.append_row([
#             platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
#         ])

#     except Exception as e:
#         print("❌ save_token error:", str(e))


def get_latest_token(platform, account_id):
    try:
        records = sheet.get_all_records()
        account_id_str = str(account_id).strip()
        print(f"Searching token for {platform}:{account_id_str}")
        for record in records:
            print(record.get("platform"), record.get("account_id"))
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
def auto_refresh_token(platform, account_id, force=False):
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

    if not expired and not force:
        return token_data["access_token"]

    # 🔄 ถ้า force == True หรือหมดอายุจริง
    try:
        if platform == "shopee":
            from services.shopee_auth import refresh_shopee_token as shopee_refresh_token
            print(f"🔄 Trying to refresh Shopee token for shop_id={account_id}")
            new_data = shopee_refresh_token(token_data["refresh_token"], account_id)

            if not new_data or "access_token" not in new_data:
                print(f"❌ Shopee refresh failed. Response: {new_data}")
                return None

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
                print("Token Data Fetched:", token_data)
                return new_data["access_token"]


        else:
            print(f"❌ Auto-refresh not implemented for {platform}")
            return token_data["access_token"]

    except Exception as e:
        print(f"❌ Auto-refresh failed for {platform}:{account_id} - {str(e)}")
        return None

