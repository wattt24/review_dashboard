
# getshopeelazada.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.token_manager import save_token
from fastapi.responses import Response
from services.shopee_auth import shopee_get_authorization_url,shopee_get_access_token
from api.shopee_api import shopee_get_categories 
from services.lazada_auth import lazada_generate_sign ,lookup_store_from_state, lazada_save_state_mapping_to_sheet,lazada_generate_state
from utils.config import SHOPEE_SHOP_ID, LAZADA_CLIENT_ID, LAZADA_REDIRECT_URI, LAZADA_CLIENT_SECRET, GOOGLE_SHEET_ID
from fastapi import FastAPI
import urllib
# GOOGLE_SHEET_ID  = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"
from fastapi.responses import JSONResponse
from utils.token_manager import *
app = FastAPI(title="Fujika Dashboard API")
import requests
import time
# from services import shopee_auth
from utils.config import SHOPEE_SHOP_ID
@app.get("/")
async def root():
    
    return {"message": "Service is running"}
@app.get("/shopee/authorize")
async def shopee_authorize():
    """
    คืน URL ให้ร้านค้ากด authorize
    """
    url = shopee_get_authorization_url()  # <-- ใช้ฟังก์ชันใหม่
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
        token_response = shopee_get_access_token(shop_id=shop_id, code=code)
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
            "message": "✅ Token saved successfully to Google Sheet.",
            "shop_id": shop_id,     
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
@app.get("/shopee/categories")
def show_shopee_categories():
    token_data = get_latest_token("shopee", SHOPEE_SHOP_ID)  # <-- ใช้ฟังก์ชันใหม่
    access_token = token_data["access_token"]
    data = shopee_get_categories(access_token, SHOPEE_SHOP_ID)
    return data.get("response", {}).get("category_list", [])


# #facebook
# @app.get("/facebook/pages")
# def get_facebook_pages():
#     page_tokens = get_all_page_tokens()
#     result = {}

#     for page_id, token in page_tokens.items():
#         url = "https://graph.facebook.com/v17.0/me/accounts"
#         resp = requests.get(url, params={"access_token": token}).json()
#         result[page_id] = resp

#     return JSONResponse(result)

#  getshopeelazada.py
@app.get("/lazada/auth/{store_id}")
async def lazada_auth(store_id: str):
    # สร้าง state ที่ unique
    state = lazada_generate_state(store_id)
    lazada_save_state_mapping_to_sheet(state, store_id)

    redirect_uri = LAZADA_REDIRECT_URI
    auth_url = (
        f"https://auth.lazada.com/oauth/authorize?"
        f"response_type=code"
        f"&client_id={LAZADA_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&force_auth=true"
        f"&country=th"
    )


    print(f"Generated state for store {store_id}: {state}")
    print(f"Redirecting to Lazada auth URL: {auth_url}")
    print(f"redirect_uri: {redirect_uri}")
    return RedirectResponse(auth_url, status_code=302)


# Step 2: Lazada callback
@app.get("/lazada/callback")
async def lazada_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return HTMLResponse("❌ Authorization canceled.", status_code=400)

    print(f"Callback received code={code}, state={state}")

    token_url = "https://auth.lazada.com/rest/auth/token/create"

    payload = {
        "app_key": LAZADA_CLIENT_ID,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": LAZADA_REDIRECT_URI,   # ไม่ต้อง encode
        "sign_method": "sha256",
    }
    payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

    print("Payload:", payload)

    resp = requests.post(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("DEBUG payload:", payload)
    print("DEBUG status:", resp.status_code)
    print("DEBUG response:", resp.text)
    print("Authorization Code:", code)
    print("Shop ID:", state)
    print("DEBUG Response status:", resp.status_code)
    print("DEBUG Response text:", resp.text)

    data = resp.json()

    if "access_token" not in data:
        return HTMLResponse(f"❌ Failed to obtain token: {data}", status_code=500)

    # mapping state → store_id
    store_id = lookup_store_from_state(state)
    if store_id:
        save_token(
            "lazada",
            store_id,
            data["access_token"],
            data.get("refresh_token", ""),
            data.get("expires_in", 0),
            data.get("refresh_expires_in", 0)
        )
        return HTMLResponse(f"✅ Token saved for store {store_id}")
    else:
        return HTMLResponse("⚠️ State mapping not found, token not saved")
