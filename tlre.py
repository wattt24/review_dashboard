import requests
import time
import hashlib
import hmac
import urllib.parse
import json
import sys
import os
import datetime
os.environ["GOOGLE_SHEET_ID"] = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"
from utils.token_manager import get_latest_token, save_token
# from utils.config import LAZADA_APP_ID, LAZADA_APP_SECRET
import requests
# ****************************ใช้ได้
from lazop.base import LazopClient, LazopRequest
import json
# ====== ตั้งค่าพื้นฐาน (ควรเก็บไว้ในที่ปลอดภัย ไม่ใช่ในโค้ด) ======
# ค่าเหล่านี้เป็นตัวอย่าง ซึ่งอาจไม่ถูกต้องในความเป็นจริง และควรเก็บไว้เป็นความลับ
LALA=100200610
LAZADA_APP_ID = "135259"
LAZADA_APP_SECRET = "MXZ9vzVVw3TsGbal73a3PljVprysSRrN" 
# LAZADA_ACCESS_TOKEN = "50000300c32t6FEoxrr98dk0ejxhvvjcjCSesUzFflPL153b42e63GwXGwiEvSgU"
import json
import requests
import time
import hashlib
import hmac
import urllib.parse
import datetime
from lazop.base import LazopClient, LazopRequest
# # ตัวกลาง sdk ในการเรียก Lazada API
# def call_lazada_api(endpoint, method="GET", params=None):
#     """
#     ฟังก์ชันกลางสำหรับเรียก Lazada API ผ่าน SDK
#     """
#     try:
#         client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
#         request = LazopRequest(endpoint, method)

#         if params:
#             for k, v in params.items():
#                 request.add_api_param(k, str(v))

#         response = client.execute(request, LAZADA_ACCESS_TOKEN)

#         # ✅ บาง SDK จะคืน dict, บางตัวคืน string
#         if isinstance(response.body, (str, bytes)):
#             data = json.loads(response.body)
#         else:
#             data = response.body

#         return data

#     except Exception as e:
#         print(f"❌ Error calling Lazada API: {str(e)}")
#         return {"error": str(e)}

def call_lazada_api(endpoint, method="GET", params=None, account_id=LALA):
    """
    เรียก Lazada API ผ่าน SDK
    ดึง access_token ล่าสุดจาก Google Sheet
    """
    try:
        # ดึง token ล่าสุดจาก Google Sheet
        token_data = get_latest_token("lazada", account_id)
        if not token_data or not token_data.get("access_token"):
            raise ValueError("❌ ไม่พบ Lazada access_token ใน Google Sheet")

        access_token = token_data["access_token"]

        # สร้าง client Lazop
        client = LazopClient("https://api.lazada.co.th/rest", LAZADA_APP_ID, LAZADA_APP_SECRET)
        request = LazopRequest(endpoint, method)

        if params:
            for k, v in params.items():
                request.add_api_param(k, str(v))

        response = client.execute(request, access_token)

        # บาง SDK คืน dict, บางตัวคืน string
        if isinstance(response.body, (str, bytes)):
            data = json.loads(response.body)
        else:
            data = response.body

        return data

    except Exception as e:
        print(f"❌ Error calling Lazada API: {str(e)}")
        return {"error": str(e)}

def lazada_refresh_access_token(account_id):
    """
    🔄 รีเฟรช Lazada Access Token ผ่าน Lazop SDK และบันทึกลง Google Sheet
    """
    # ดึง refresh_token ล่าสุดจาก Google Sheet
    token_data = get_latest_token(platform="lazada", account_id=seller_id)
    if not token_data or not token_data.get("refresh_token"):
        print(f"❌ ไม่พบ refresh_token สำหรับ account_id {account_id}")
        return None

    refresh_token = token_data["refresh_token"]

    print("\n================ Lazada API Debug Info ================")
    print(f"🔹 API Name: /auth/token/refresh")
    print(f"🔹 Refresh Token: {refresh_token}")
    print(f"🔹 Account ID: {seller_id}")
    print("=======================================================\n")

    # เรียกผ่าน SDK ด้วยฟังก์ชันกลาง
    response = call_lazada_api(
        endpoint="/auth/token/refresh",
        method="POST",
        params={"refresh_token": refresh_token}
    )

    # ตรวจสอบผลลัพธ์
    if not response:
        print("❌ ไม่พบข้อมูล response จาก Lazada SDK")
        return None

    data = response.get("data") or response  # บาง SDK ห่ออยู่ใน "data"

    access_token = data.get("access_token")
    new_refresh = data.get("refresh_token")
    expires_in = data.get("expires_in")

    if access_token and new_refresh:
        
        seller_id = data.get("account")  # Lazada seller ID
        save_token(
            platform="lazada",
            account_id=seller_id,
            access_token=access_token,
            refresh_token=new_refresh,
            expires_in=expires_in
        )
        expire_time = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        print(f"✅ Lazada token refreshed successfully (expires at {expire_time})")
    else:
        print("❌ Failed to refresh Lazada access token:", response)

    return response
