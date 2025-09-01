# services/gsc_fujikathailand.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import json
import os
from datetime import date, timedelta

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "sc-domain:fujikathailand.com"

def get_gsc_data(start_date="2025-08-01", end_date="2025-08-28"):
    try:
        # โหลด credentials จาก environment variable
        service_account_info = json.loads(os.environ["SERVICE_AC"])
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )

        # สร้าง service
        webmasters_service = build("searchconsole", "v1", credentials=credentials)

        # Request
        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 10
        }

        response = webmasters_service.searchanalytics().query(
            siteUrl=SITE_URL, body=request
        ).execute()

        rows = response.get("rows", [])
        if not rows:
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
        print(f"❌ Error fetching GSC data: {e}")
        return pd.DataFrame(columns=["query", "clicks", "impressions", "ctr", "position"])
