from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services.test_auth import get_token, save_token
import os

app = FastAPI()

@app.get("/shopee/callback")
async def shopee_callback(request: Request):
    """
    Endpoint ที่ Shopee redirect กลับมา หลัง user login
    รับ query parameter: code, shop_id
    """
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if not code or not shop_id:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "msg": "Missing code or shop_id"}
        )

    shop_id = int(shop_id)

    # เรียกฟังก์ชัน get_token เพื่อแลก access token
    token_data = get_token(code, shop_id)

    if "access_token" in token_data:
        # บันทึก token ลง Google Sheet
        save_token(
            shop_id,
            token_data["access_token"],
            token_data["refresh_token"],
            token_data["expires_in"],
            token_data["refresh_expires_in"]
        )
        return {"status": "success", "msg": "✅ Access token saved to Google Sheet"}
    else:
        return {"status": "error", "msg": f"❌ Failed to get token: {token_data}"}