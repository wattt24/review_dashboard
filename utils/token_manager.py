# เอาไว้จัดการ Google Sheet เป็นศูนย์กลาง token ของทุกแพลตฟอร์ม (Shopee, Lazada, Facebook ฯลฯ)
# utils/token_manager.py
import os
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

# ===== Google Sheet Setup =====
key_path = "/etc/secrets/SERVICE_ACCOUNT_JSON"
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

if not os.path.exists(key_path):
    raise FileNotFoundError(f"Credential file not found at {key_path}")

credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(os.environ["GOOGLE_SHEET_ID"]).sheet1

# ===== Token Manager =====
def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
    """บันทึกหรืออัปเดต token ลง Google Sheet"""
    expired_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
    refresh_expired_at = (datetime.now() + timedelta(seconds=refresh_expires_in)).isoformat() if refresh_expires_in else ""

    try:
        # หา row เดิมจาก account_id + platform
        records = sheet.get_all_records()
        for idx, record in enumerate(records, start=2):  # row 2 เป็นต้นไป (row1 header)
            if record["platform"] == platform and str(record["account_id"]) == str(account_id):
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
    """ดึง token ล่าสุดของ platform + account_id"""
    try:
        records = sheet.get_all_records()
        for record in records:
            if record["platform"] == platform and str(record["account_id"]) == str(account_id):
                return {
                    "access_token": record["access_token"],
                    "refresh_token": record["refresh_token"],
                    "expired_at": record.get("expired_at"),
                    "refresh_expired_at": record.get("refresh_expired_at")
                }
    except Exception as e:
        print("❌ get_latest_token error:", str(e))

    return None
