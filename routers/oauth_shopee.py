# routers/oauth_shopee.py

from fastapi import APIRouter, Request
import time, hmac, hashlib
import requests
import os
from dotenv import load_dotenv

from database.session import SessionLocal
from services.shopee_token_service import save_token_to_db

load_dotenv()

router = APIRouter()

@router.get("/auth/shopee/callback")
async def shopee_callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")
    
    if not code or not shop_id:
        return {"error": "Missing code or shop_id"}

    # ====== เตรียมข้อมูล ======
    partner_id = int(os.getenv("SHOPEE_PARTNER_ID"))
    partner_key = os.getenv("SHOPEE_PARTNER_KEY")
    redirect_url = os.getenv("SHOPEE_REDIRECT_URL")
    path = "/api/v2/auth/token/get"
    timestamp = int(time.time())

    # ====== สร้าง sign ======
    base_string = f"{partner_id}{path}{timestamp}{code}{shop_id}"
    sign = hmac.new(
        partner_key.encode(), base_string.encode(), hashlib.sha256
    ).hexdigest()

    # ====== ส่ง POST เพื่อแลก token ======
    url = f"https://partner.shopeemobile.com{path}"
    body = {
        "code": code,
        "shop_id": int(shop_id),
        "partner_id": partner_id,
        "sign": sign,
        "timestamp": timestamp
    }

    response = requests.post(url, json=body)
    result = response.json()

    # ✅ บันทึกลงฐานข้อมูล
    db = SessionLocal()
    save_token_to_db(
        db,
        shop_id=shop_id,
        access_token=result.get("access_token"),
        refresh_token=result.get("refresh_token"),
        expire_in=result.get("expire_in"),
    )
    db.close()

    return {
        "platform": "shopee",
        "shop_id": shop_id,
        "access_token": result.get("access_token"),
        "expire_in": result.get("expire_in"),
        "refresh_token": result.get("refresh_token"),
    }
