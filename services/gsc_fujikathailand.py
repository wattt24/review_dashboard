# import os
# import pandas as pd
# from googleapiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
# KEY_FILE = os.path.join("data","review-dashboard-service-7304afdb2e7e.json")
# SITE_URL = "https://www.fujikathailand.com"  # เว็บของคุณ

# credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE, SCOPES)
# service = build("searchconsole", "v1", credentials=credentials)

# request = {
#     "startDate": "2025-07-01",
#     "endDate": "2025-07-31",
#     "dimensions": ["query"],
#     "rowLimit": 10
# }

# response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()

# rows = response.get("rows", [])
# data = [{"query": r["keys"][0], "clicks": r["clicks"], "impressions": r["impressions"],
#          "ctr": r["ctr"], "position": r["position"]} for r in rows]

# df = pd.DataFrame(data)
# print(df)
