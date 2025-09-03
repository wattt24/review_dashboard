# services/gsc_fujikathailand.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import streamlit as st
import traceback
from datetime import date, timedelta

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# ✅ ถ้าเป็น domain property ให้ใช้ sc-domain
SITE_URL = "sc-domain:fujikathailand.com"
# ถ้าเป็น URL-prefix property ให้ใช้:
#SITE_URL = "https://fujikathailand.com/"

def get_last_week_dates():
    """คืนค่า start_date, end_date ของสัปดาห์ที่แล้ว (จันทร์–อาทิตย์)"""
    today = date.today()
    # หาวันจันทร์ของสัปดาห์นี้
    this_monday = today - timedelta(days=today.weekday())
    # หาวันจันทร์ของสัปดาห์ที่แล้ว
    last_monday = this_monday - timedelta(days=7)
    # วันอาทิตย์ของสัปดาห์ที่แล้ว
    last_sunday = this_monday - timedelta(days=1)
    return last_monday.isoformat(), last_sunday.isoformat()

def get_gsc_data():
    try:
        start_date, end_date = get_last_week_dates()

        # โหลด credentials จาก Streamlit secrets
        service_account_info = dict(st.secrets["SERVICE_AC"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )

        # สร้าง service
        webmasters_service = build("searchconsole", "v1", credentials=credentials)

        # Request body
        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 10
        }

        response = webmasters_service.searchanalytics().query(
            siteUrl=SITE_URL, body=request
        ).execute()
        print(response)
        print(f"📅 Fetching GSC data from {start_date} to {end_date}")
        print("🔍 Raw Response:", response)

        rows = response.get("rows", [])
        if not rows:
            print("⚠️ No rows found in GSC response")
            return pd.DataFrame(columns=["query", "clicks", "impressions", "ctr", "position"])

        df = pd.DataFrame([
            {
                "query": row["keys"][0] if "keys" in row and row["keys"] else None,
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": row.get("ctr", 0),
                "position": row.get("position", 0),
            }
            for row in rows
        ])
        return df

    except Exception as e:
        print("❌ Error fetching GSC data:", e)
        print(traceback.format_exc())  # แสดง traceback เต็มใน log
        return pd.DataFrame(columns=["query", "clicks", "impressions", "ctr", "position"])
