
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
@router.get("/shopee/callback")
async def shopee_callback(request: Request):
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"

    # sign ตาม doc
    sign_input = f"{SHOPEE_PARTNER_ID}{path}{timestamp}{code}{shop_id}"
    sign = hmac.new(
        SHOPEE_PARTNER_SECRET.encode("utf-8"),
        sign_input.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    url = f"{BASE_URL}{path}?partner_id={SHOPEE_PARTNER_ID}&timestamp={timestamp}&sign={sign}"

    payload = {
        "code": code,
        "shop_id": int(shop_id)
    }

    print("=== DEBUG Shopee Access Token ===")
    print("Partner ID:", SHOPEE_PARTNER_ID)
    print("Shop ID:", shop_id)
    print("Code:", code)
    print("Timestamp:", timestamp)
    print("Sign Input String:", sign_input)
    print("Generated Sign:", sign)
    print("Request URL:", url)
    print("Request Payload:", payload)
    print("================================")

    resp = requests.post(url, json=payload)
    print("=== DEBUG Shopee Response ===")
    print(resp.json())
    print("=============================")

    return resp.json()
# @app.get("/shopee/callback")
# async def shopee_callback(code: str = None, shop_id: int = None):
#     if not code or not shop_id:
#         return {"message": "Shopee callback ping"}

#     print("Authorization Code:", code)
#     print("Shop ID:", shop_id)

#     try:
#         # ใช้ฟังก์ชันแลก token ที่ถูกต้อง
#         token_response = shopee_get_access_token(shop_id=shop_id, code=code)

#         return {
#             "message": "✅ Token saved successfully.",
#             "token": {
#                 "access_token": token_response["access_token"],
#                 "refresh_token": token_response["refresh_token"],
#                 "expire_in": token_response.get("expire_in"),
#                 "refresh_expires_in": token_response.get("refresh_expires_in")
#             }
#         }

#     except ValueError as e:
#         return {
#             "error": "Invalid authorization code. Please try again.",
#             "details": str(e)
#         }

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