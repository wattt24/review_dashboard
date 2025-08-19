
from fastapi import FastAPI, Request
from services.shopee_auth import get_token

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "Shopee Backend is running"}

@app.get("/shopee/callback")
def shopee_callback(code: str, shop_id: int, main_account_id: int = None):
    """รับ code หลังจากร้าน authorize แล้ว"""
    token_data = get_token(code, shop_id)

    # TODO: เก็บลง Database (access_token, refresh_token, expire_in, shop_id)
    return {
        "status": "success",
        "shop_id": shop_id,
        "token_data": token_data
    }
