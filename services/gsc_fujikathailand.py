from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import date, timedelta
import json
import os
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
SITE_URL = "sc-domain:fujikathailand.com"

# โหลด credentials จาก environment variable
service_account_info = json.loads(os.environ["SERVICE_AC"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)

# ✅ ตรงนี้แหละที่ต้องสร้าง service object
webmasters_service = build("searchconsole", "v1", credentials=credentials)

# ตัวอย่าง request
request = {
    "startDate": "2025-08-01",
    "endDate": "2025-08-28",
    "dimensions": ["query"],
    "rowLimit": 10
}

# เรียก API
response = webmasters_service.searchanalytics().query(
    siteUrl=SITE_URL, body=request
).execute()
