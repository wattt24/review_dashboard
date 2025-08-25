# getshopeelazada.py
from fastapi import FastAPI
from services.test_auth import get_token, save_token
import os

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "Shopee Backend is running"}

@app.get("/exchange_token")
def exchange_token():
    CODE = os.environ.get("SHOPEE_CODE")
    SHOP_ID = int(os.environ.get("SHOPEE_SHOP_ID"))

    token_data = get_token(CODE, SHOP_ID)

    if "access_token" in token_data:
        save_token(
            SHOP_ID,
            token_data["access_token"],
            token_data["refresh_token"],
            token_data["expires_in"],
            token_data["refresh_expires_in"]
        )
        return {"status": "success", "msg": "✅ Access token saved to Google Sheet"}
    else:
        return {"status": "error", "msg": f"❌ Failed to get token: {token_data}"}
