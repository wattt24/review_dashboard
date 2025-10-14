# เอาไว้เก็บลง Google Sheet เป็นศูนย์กลาง token ของทุกแพลตฟอร์ม (Shopee, Lazada, Facebook ฯลฯ) 
# utils/token_manager.py
import os , json
import pandas as pd
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials 
import streamlit as st

# ===== Google Sheet Setup =====
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
# utils/token_manager.py
#ใช้เชื่อมต่อ Google Sheet
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

# ===== Connect to Google Sheets =====
client = get_gspread_client()

# โหลด Sheet ID (มีแค่ตัวเดียว)
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID") or st.secrets.get("GOOGLE_SHEET_ID")

if not GOOGLE_SHEET_ID:
    st.error("❌ ไม่พบ GOOGLE_SHEET_ID ใน environment หรือ st.secrets")
else:
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# ===== Utility functions =====
def get_sheet():
    """คืนค่า gspread sheet object"""
    if not GOOGLE_SHEET_ID:
        raise ValueError("❌ GOOGLE_SHEET_ID not found in environment or secrets.")
    return client.open_by_key(GOOGLE_SHEET_ID).sheet1

# คำสะั่งไว้เรียกGOOGLE_SHEET_ID ใช้ sheet1 = get_sheet("form1")
# เรียกCONTACT_INFORMATION_SHEET_ID ใช้ sheet2 = get_sheet("form2")
def sheet_to_df(sheet):
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    return df


# บันทึก Token ลง Google Sheet
def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
    try:
        sheet = get_sheet()  # โหลด sheet ทุกครั้งที่บันทึก
        now = datetime.now()
        expired_at = (now + timedelta(seconds=expires_in)).isoformat() if expires_in else ""
        refresh_expired_at = ""
        if platform.lower() == "shopee":
            refresh_expired_at = (now + timedelta(days=30)).isoformat()
        elif refresh_expires_in:
            refresh_expired_at = (now + timedelta(seconds=refresh_expires_in)).isoformat()

        account_id_str = str(account_id).strip()

        # หาแถวที่ตรงกับ platform + account_id
        try:
            cell_platform = sheet.find(str(platform).strip(), in_column=1)
            row_idx = cell_platform.row
            if str(sheet.cell(row_idx, 2).value).strip() == account_id_str:
                sheet.update(f"A{row_idx}:G{row_idx}", [[
                    platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
                ]])
                print(f"✅ Updated existing token row {row_idx}")
                return
        except gspread.CellNotFound:
            pass  # ไม่เจอแถวที่ตรงกัน

        # ถ้าไม่เจอแถว append ใหม่
        sheet.append_row([
            platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
        ])
        print("✅ Appended new token row")

    except Exception as e:
        print(f"❌ Exception in save_token: {e}")
# def save_token(platform, account_id, access_token, refresh_token, expires_in=None, refresh_expires_in=None):
#     now = datetime.now()
#     # Access Token expiry
#     expired_at = (now + timedelta(seconds=expires_in)).isoformat() if expires_in else ""

#     # Refresh Token expiry
#     refresh_expired_at = ""
#     if platform.lower() == "shopee":
#         # Shopee refresh token มีอายุ 30 วัน → คำนวณเอง
#         refresh_expired_at = (now + timedelta(days=30)).isoformat()
#     elif refresh_expires_in:  
#         # Lazada หรือ platform อื่นที่ส่งค่ามา
#         refresh_expired_at = (now + timedelta(seconds=refresh_expires_in)).isoformat()

#     account_id_str = str(account_id).strip()
    
#     try:
#     # ค้นหาแถวที่ตรงกับ platform + account_id
#         cell_platform = sheet.find(str(platform).strip(), in_column=1)  # สมมติ platform อยู่ column A
#         row_idx = cell_platform.row
#         # ตรวจสอบ account_id ด้วย
#         if str(sheet.cell(row_idx, 2).value).strip() == account_id_str:  # account_id column B
#             # update แถว
#             sheet.update(f"A{row_idx}:G{row_idx}", [[
#                 platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
#             ]])
#             return
#     except gspread.CellNotFound:
#         # ถ้าไม่เจอ → append row ใหม่
#         sheet.append_row([
#             platform, account_id_str, access_token, refresh_token, expired_at, refresh_expired_at, datetime.now().isoformat()
#         ])


# ดึง Token ล่าสุด
def get_latest_token(platform, account_id):
    try:
        sheet = get_sheet()
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


