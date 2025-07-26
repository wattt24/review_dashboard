import os
import time
import hmac
import hashlib
import httpx

PARTNER_ID = os.getenv("SHOPEE_PARTNER_ID")
PARTNER_KEY = os.getenv("SHOPEE_PARTNER_KEY")
REDIRECT_URI = os.getenv("SHOPEE_REDIRECT_URI")
BASE_URL = "https://partner.shopeemobile.com"

# ตรวจสอบ ENV
if not all([PARTNER_ID, PARTNER_KEY, REDIRECT_URI]):
    raise EnvironmentError("Missing Shopee ENV variables.")

async def exchange_token(code: str):
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    url = BASE_URL + path

    base_string = f"{PARTNER_ID}{path}{timestamp}"
    sign = hmac.new(PARTNER_KEY.encode(), base_string.encode(), hashlib.sha256).hexdigest()

    payload = {
        "code": code,
        "partner_id": int(PARTNER_ID),
        "sign": sign,
        "timestamp": timestamp,
        "redirect": REDIRECT_URI,
    }

    headers = {
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()["data"]
        except httpx.HTTPStatusError as e:
            content = e.response.text
            raise Exception(f"HTTP error {e.response.status_code}: {content}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
