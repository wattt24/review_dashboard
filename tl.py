import time, hashlib, hmac, requests
LAZADA_CLIENT_ID = "ใส่ app_key ของคุณ"
LAZADA_CLIENT_SECRET = "ใส่ app_secret ของคุณ"
LAZADA_REDIRECT_URI = "https://review-dashboard-ccvk.onrender.com/lazada/callback"
code = "0_135259_8QDVXX4gPcG6ipyUvDNOJWSx365"
from utils.config import LAZADA_APP_ID, LAZADA_APP_SECRET   

def lazada_exchange_token(code: str):
    """
    แลก authorization code จาก Lazada เพื่อขอ access_token และ refresh_token
    """
    try:
        url = "https://auth.lazada.com/rest/auth/token/create"

        # Lazada ต้องการพารามิเตอร์เหล่านี้
        params = {
            "app_key": LAZADA_APP_ID,
            "timestamp": str(int(time.time() * 1000)),
            "sign_method": "sha256",
            "code": code,
        }

        # ✅ สร้าง signature ตามที่ Lazada กำหนด
        # Signature = UpperCase(HMAC_SHA256(app_secret, sorted_params))
        sorted_params = "".join([f"{k}{v}" for k, v in sorted(params.items())])
        sign_base = LAZADA_APP_SECRET + sorted_params + LAZADA_APP_SECRET
        sign = hmac.new(LAZADA_APP_SECRET.encode("utf-8"), sign_base.encode("utf-8"), hashlib.sha256).hexdigest().upper()

        # เพิ่ม sign เข้าไปใน params
        params["sign"] = sign

        print("📡 Requesting Lazada token with params:", params)

        # ส่ง POST request ไปยัง API
        response = requests.post(url, data=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data

    except Exception as e:
        print("❌ Error exchanging token:", str(e))
        return {"error": str(e)}