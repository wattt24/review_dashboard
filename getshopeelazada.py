# getshopeelazada.py
from fastapi import FastAPI
from services.shopee_auth import get_token, save_token
from datetime import datetime

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "Shopee Backend is running"}

@app.get("/shopee/callback")
def shopee_callback(code: str, shop_id: int, main_account_id: int = None):
    token_data = get_token(code, shop_id)

    access_token = token_data.get("access_token")
    refresh_token_value = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")
    refresh_expires_in = token_data.get("refresh_expires_in")


    # ใช้ฟังก์ชันจาก shopee_auth.py บันทึกลง Google Sheet
    save_token(shop_id, access_token, refresh_token_value, expires_in, refresh_expires_in)

    return {
        "status": "success",
        "shop_id": shop_id,
        "token_data": token_data
    }
