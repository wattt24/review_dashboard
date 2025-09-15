import gspread
from datetime import datetime
import os

# ใช้ Service Account JSON (โหลดจาก st.secrets หรือไฟล์)
SERVICE_ACCOUNT_FILE = "service_account.json"  # หรือใช้ st.secrets["gcp_service_account"]

SHEET_NAME = "tokens"  # ชื่อ Google Sheet
WORKSHEET_NAME = "Sheet1"  # แผ่นงาน

def get_token(platform: str, account_id: str = None):
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    sh = gc.open(SHEET_NAME)
    ws = sh.worksheet(WORKSHEET_NAME)
    records = ws.get_all_records()

    # filter platform + account_id
    for row in records:
        if row["platform"] == platform:
            if account_id is None or str(row["account_id"]) == str(account_id):
                return row["access_token"]

    raise ValueError(f"❌ ไม่พบ token ของ {platform} (account_id={account_id})")
