
# getshopeelazada.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from utils.token_manager import save_token, get_gspread_client
from fastapi.responses import Response
from services.shopee_auth import shopee_get_authorization_url,shopee_get_access_token
from api.shopee_api import shopee_get_categories 
from services.lazada_auth import lazada_generate_sign ,lazada_get_auth_url_for_store
from utils.config import SHOPEE_SHOP_ID, LAZADA_CLIENT_ID, LAZADA_REDIRECT_URI, LAZADA_CLIENT_SECRET, GOOGLE_SHEET_ID
from fastapi import FastAPI
# GOOGLE_SHEET_ID  = "113NflRY6A8qDm5KmZ90bZSbQGWaNtFaDVK3qOPU8uqE"
from fastapi.responses import JSONResponse
from utils.token_manager import *
from services.facebook_auth import get_all_page_tokens
app = FastAPI(title="Fujika Dashboard API")
import requests
import time
# from services import shopee_auth
from utils.config import SHOPEE_SHOP_ID
from utils.token_manager import auto_refresh_token
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
def lookup_store_from_state(state):
    # ตัวอย่าง: ดึงจาก Google Sheet 'state_mapping'
    client = get_gspread_client()
    ss = client.open_by_key(GOOGLE_SHEET_ID)
    try:
        ws = ss.worksheet("state_mapping")
    except Exception:
        return None
    records = ws.get_all_records()
    for r in records:
        if r.get("state") == state:
            return r.get("store_id")
    return None

#  getshopeelazada.py
@app.get("/lazada/auth/{store_id}")
async def lazada_auth_redirect(store_id: str):
    url = lazada_get_auth_url_for_store(store_id)
    return RedirectResponse(url)
@app.get("/lazada/callback")
async def lazada_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("Authorization canceled.", status_code=400)

    token_url = "https://auth.lazada.com/rest/auth/token"

    timestamp = int(time.time() * 1000)

    payload = {
        "app_key": LAZADA_CLIENT_ID,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": LAZADA_REDIRECT_URI,
        "timestamp": int(time.time() * 1000),
        "sign_method": "sha256"
    }
    payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

    resp = requests.post(token_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    data = resp.json()
    print("DEBUG Response:", data)

    if "access_token" not in data:
        return HTMLResponse(f"❌ Failed to obtain token: {data}", status_code=500)
@app.get("/lazada/callback")
async def lazada_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code:
        return HTMLResponse("Authorization canceled.", status_code=400)

    token_url = "https://auth.lazada.com/rest/auth/token"
    timestamp = int(time.time() * 1000)
    
    payload = {
        "app_key": LAZADA_CLIENT_ID,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": LAZADA_REDIRECT_URI,
        "timestamp": timestamp,
        "sign_method": "sha256"
    }
    payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

    resp = requests.post(token_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    data = resp.json()
    print("DEBUG Response:", data)

    if "access_token" not in data:
        return HTMLResponse(f"❌ Failed to obtain token: {data}", status_code=500)

    # 🔹 Lookup store_id จาก state
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
        print(f"✅ Lazada token saved for store {store_id}")
    else:
        print("⚠️ State mapping not found, token not saved")
    return HTMLResponse(f"✅ Token obtained: {data['access_token']}")
# @app.get("/lazada/callback")
# async def lazada_callback(request: Request):
#     code = request.query_params.get("code")
#     state = request.query_params.get("state")
#     if not code:
#         return HTMLResponse("Authorization canceled or no code returned.", status_code=400)

#     # ตรวจสอบ state → หา store_id
#     store_id = lookup_store_from_state(state)

#     # 1) เตรียม payload
#     token_url = "https://auth.lazada.com/rest/auth/token"
#     timestamp = int(time.time() * 1000)

#     payload = {
#         "app_key": LAZADA_CLIENT_ID,
#         "sign_method": "sha256",
#         "timestamp": timestamp,
#         "code": code,
#         "grant_type": "authorization_code",
#         "redirect_uri": LAZADA_REDIRECT_URI,
#     }

#     # 2) สร้าง sign
#     payload["sign"] = lazada_generate_sign(payload, LAZADA_CLIENT_SECRET)

#     # 3) ส่ง request
#     resp = requests.post(token_url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
#     data = resp.json()
#     print("DEBUG Response:", data)

#     if "access_token" not in data:
#         return HTMLResponse(f"❌ Failed to obtain token: {data}", status_code=500)

#     access_token = data["access_token"]
#     refresh_token = data.get("refresh_token")
#     expires_in = data.get("expires_in")
#     refresh_expires_in = data.get("refresh_expires_in")

#     # 4) ตรวจสอบร้านค้า
#     seller_info = None
#     try:
#         seller_resp = requests.get(
#             "https://api.lazada.com/rest/seller/get",
#             params={"app_key": LAZADA_CLIENT_ID, "timestamp": int(time.time() * 1000), "sign_method": "sha256"},
#             headers={"Authorization": f"Bearer {access_token}"}
#         )
#         seller_info = seller_resp.json()
#     except Exception as e:
#         seller_info = {"error": str(e)}

#     shop_id = None
#     if isinstance(seller_info, dict):
#         shop_id = seller_info.get("sellerId") or seller_info.get("data", {}).get("shopId")

#     account_id_to_save = shop_id or store_id or "unknown"

#     # 5) บันทึก token
#     save_token(
#         platform="lazada",
#         account_id=account_id_to_save,
#         access_token=access_token,
#         refresh_token=refresh_token,
#         expires_in=expires_in,
#         refresh_expires_in=refresh_expires_in
#     )

#     return HTMLResponse(f"✅ เชื่อมต่อ Lazada สำเร็จสำหรับร้าน: {account_id_to_save}")


