
import time
import hmac
import hashlib
import requests

LAZADA_APP_ID = "135259"
LAZADA_APP_SECRET = "MXZ9vzVVw3TsGbal73a3PljVprysSRrN"  # <-- แทนที่ด้วย secret จริงของคุณ
LAZADA_REDIRECT_URI = "https://review-dashboard-ccvk.onrender.com/lazada/callback"

def lazada_exchange_token(code: str):
    """
    แลก authorization code จาก Lazada เพื่อขอ access_token และ refresh_token
    ตามมาตรฐานการเซ็น /auth/token/create
    """
    try:
        path = "/auth/token/create"
        url = f"https://auth.lazada.com/rest{path}"

        # ✅ ขั้นตอน 1: กำหนดพารามิเตอร์ที่ Lazada ต้องการ
        params = {
            "app_key": LAZADA_APP_ID,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": LAZADA_REDIRECT_URI,
            "sign_method": "sha256",
            "timestamp": str(int(time.time() * 1000))
        }

        # ✅ ขั้นตอน 2: เรียงพารามิเตอร์ตามชื่อ (A-Z)
        sorted_items = sorted(params.items())
        concatenated = ''.join([f"{k}{v}" for k, v in sorted_items])

        # ✅ ขั้นตอน 3: ต่อ path ด้านหน้า แล้วเข้ารหัสด้วย HMAC-SHA256
        base_string = path + concatenated
        sign = hmac.new(
            LAZADA_APP_SECRET.encode("utf-8"),
            base_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest().upper()

        # ✅ ขั้นตอน 4: ใส่ sign กลับเข้า params
        params["sign"] = sign

        print("📡 Base string:", base_string)
        print("✅ Sign:", sign)
        print("📤 Sending request with params:", params)

        # ✅ ขั้นตอน 5: ส่ง POST request ไปที่ Lazada
        response = requests.post(url, data=params, timeout=10)
        data = response.json()

        print("🔹 Lazada token response:", data)
        return data

    except Exception as e:
        print("❌ Error exchanging token:", str(e))
        return {"error": str(e)}
