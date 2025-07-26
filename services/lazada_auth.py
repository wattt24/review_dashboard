import os
import time
import hashlib
import httpx

# โหลดค่าจาก environment
LAZADA_APP_KEY = os.getenv("LAZADA_APP_KEY")
LAZADA_APP_SECRET = os.getenv("LAZADA_APP_SECRET")
LAZADA_REDIRECT_URI = os.getenv("LAZADA_REDIRECT_URI")
BASE_URL = "https://auth.lazada.com/rest"

# ตรวจสอบ ENV
if not all([LAZADA_APP_KEY, LAZADA_APP_SECRET, LAZADA_REDIRECT_URI]):
    raise EnvironmentError("Missing Lazada ENV variables.")

async def exchange_lazada_token(code: str):
    """
    ใช้ code ที่ Lazada ส่งมาเพื่อแลก access_token
    Lazada OAuth2 - Authorization Code Grant
    """
    path = "/auth/token/create"
    url = BASE_URL + path

    # สร้าง payload ตาม Lazada spec
    payload = {
        "app_key": LAZADA_APP_KEY,
        "app_secret": LAZADA_APP_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": LAZADA_REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, data=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()  # ข้อมูลจะมี access_token, refresh_token, expire_in, etc.
        except httpx.HTTPStatusError as e:
            content = e.response.text
            raise Exception(f"HTTP error {e.response.status_code}: {content}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
