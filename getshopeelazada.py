# getshopeelazada.py
from fastapi import FastAPI, Request
from services.test_auth import get_token, save_token

app = FastAPI()

@app.get("/shopee/callback")
async def shopee_callback(code: str, shop_id: str):
    tokens = get_token(code, shop_id)
    if "access_token" in tokens:
        save_token(
            shop_id,
            tokens["access_token"],
            tokens["refresh_token"],
            tokens["expires_in"],
            tokens["refresh_expires_in"]
        )
        return {"status": "ok", "shop_id": shop_id}
    else:
        return {"status": "error", "detail": tokens}