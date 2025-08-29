from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import date, timedelta
import json
import os

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

service_account_info = json.loads(os.environ["service_account"])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=SCOPES
)
SITE_URL = 'https://www.fujikathailand.com'
# ----------------- Set Date Range -----------------
end_date = date.today()
start_date = end_date - timedelta(days=30)

request = {
    'startDate': start_date.isoformat(),
    'endDate': end_date.isoformat(),
    'dimensions': ['query'],
    'rowLimit': 50  # จำนวน keyword สูงสุด
}

response = webmasters_service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()

# ----------------- แปลงเป็น DataFrame -----------------
rows = response.get('rows', [])
data = []
for row in rows:
    data.append({
        'Keyword': row['keys'][0],
        'Clicks': row.get('clicks', 0),
        'Impressions': row.get('impressions', 0),
        'CTR': row.get('ctr', 0) * 100,
        'Avg. Position': row.get('position', 0)
    })

df = pd.DataFrame(data)