import httpx
from config import LAZADA_PARTNER_ID, LAZADA_PARTNER_KEY, LAZADA_REDIRECT_URI
from models.database import SessionLocal
from models.token_model import OAuthToken

import httpx
import asyncio

async def exchange_lazada_token(code: str):
    token_url = "https://auth.lazada.com/rest/auth/token/create"
    payload = {
        "code": code,
        "client_id": LAZADA_PARTNER_ID,
        "client_secret": LAZADA_PARTNER_KEY,
        "redirect_uri": LAZADA_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=payload)
        data = response.json()

    # บันทึกลง DB (แนะนำใช้ sync/async ตาม DB ที่คุณใช้)
    db = SessionLocal()
    token = OAuthToken(
        platform="lazada",
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data["expires_in"],
    )
    db.add(token)
    db.commit()
    db.close()

    return data
