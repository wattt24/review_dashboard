
# getshopeelazada.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from services.shopee_auth import shopee_get_access_token,shopee_get_authorization_url
from services.lazada_auth import get_lazada_token, call_lazada_api
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from utils.token_manager import *
from services.facebook_auth import get_all_page_tokens
app = FastAPI(title="Fujika Dashboard API")
import requests
# from services import shopee_auth

from utils.token_manager import auto_refresh_token
@app.get("/")
async def root():
    return {"message": "Service is running"}
@app.get("/shopee/authorize")
async def shopee_authorize():
    """
    คืน URL ให้ร้านค้ากด authorize
    """
    url = shopee_get_authorization_url()  # <-- ใส่ตรงนี้
    return {"authorization_url": url}
@app.api_route("/shopee/callback", methods=["GET", "HEAD"])
async def shopee_callback(code: str = None, shop_id: int = None):
    # ฟังก์ชันนี้คือ callback endpoint ที่ Shopee จะเรียกหลังจาก user กด Allow ที่หน้า OAuth
    # Shopee จะส่ง query params: code (authorization code) และ shop_id มาที่ endpoint นี้

    if not code or not shop_id:
        # ถ้าไม่มี code หรือ shop_id แสดงว่า Shopee แค่ "ping" มาลองเรียกดู ไม่ได้ authorize จริง
        return {"message": "Shopee callback ping"}

    # debug: แสดง authorization code และ shop_id ที่ Shopee ส่งมา
    print("Authorization Code:", code)
    print("Shop ID:", shop_id)

    try:
        # 1. ใช้ code + shop_id ไปขอแลก access_token/refresh_token จาก Shopee API
        # get_token() เป็นฟังก์ชันที่คุณเขียนไว้เองเพื่อเรียก API ของ Shopee
        token_response = shopee_get_access_token(
            shop_id=shop_id,  # <-- shop_id ต้องอยู่ตัวแรก
            code=code         # <-- code อยู่ตัวหลัง
        )
        save_token(
                    platform="shopee",
                    account_id=shop_id,
                    access_token=token_response["access_token"],
                    refresh_token=token_response["refresh_token"],
                    expires_in=token_response.get("expire_in"),
                    refresh_expires_in=token_response.get("refresh_expires_in")
                )

        # 2. ถ้าแลก token สำเร็จ คืนค่ากลับไปเป็น response JSON
        return {
            "message": "✅ Token saved successfully.",
            "token": {
                "access_token": token_response["access_token"],
                "refresh_token": token_response["refresh_token"],
                "expire_in": token_response.get("expire_in"),  # อายุ access_token
                "refresh_expires_in": token_response.get("refresh_expires_in")  # อายุ refresh_token
            }
        }

    except ValueError as e:
        # ถ้าแลก token ไม่สำเร็จ เช่น code ใช้แล้ว / หมดอายุ Shopee จะ error
        # ตรงนี้ดัก error และส่งข้อความที่ user-friendly กลับไป
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid authorization code", "details": str(e)}
        )


@app.api_route("/lazada/callback", methods=["GET", "HEAD"])
async def lazada_callback(code: str = None, country: str = None):
    if not code:
        return {"message": "Lazada callback ping"}

    print("Authorization Code:", code)
    print("Country:", country)

    # 1. แลก token จริงจาก Lazada
    token_response = get_lazada_token(code)

    # 2. บันทึก token ลง Google Sheet
    account_id = token_response.get("account_id") or country  # ใช้ account_id หรือ country แทน
    save_token(
        platform="lazada",
        account_id=account_id,
        access_token=token_response["access_token"],
        refresh_token=token_response.get("refresh_token"),
        expires_in=token_response.get("expires_in"),
    )

    # 3. auto refresh ถ้าหมดอายุ
    access_token = auto_refresh_token("lazada", account_id)

    # 4. ตัวอย่างเรียก API lazada (เช่น get seller info)
    seller_info = call_lazada_api(
        path="/seller/get",
        access_token=access_token
    )

    return JSONResponse({
        "message": "Lazada callback received and token saved",
        "account_id": account_id,
        "token_response": token_response,
        "seller_info": seller_info
    })

#facebook

@app.get("/facebook/pages")
def get_facebook_pages():
    page_tokens = get_all_page_tokens()
    result = {}

    for page_id, token in page_tokens.items():
        url = "https://graph.facebook.com/v17.0/me/accounts"
        resp = requests.get(url, params={"access_token": token}).json()
        result[page_id] = resp

    return JSONResponse(result)