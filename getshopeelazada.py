
# getshopeelazada.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from services.shopee_auth import shopee_get_authorization_url,get_token,check_shop_type,call_shopee_api_auto
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
    url = shopee_get_authorization_url()
    return {"authorization_url": url}

@app.api_route("/shopee/callback", methods=["GET", "HEAD"])
async def shopee_callback(code: str = None, shop_id: int = None):
    if not code or not shop_id:
        return {"message": "Shopee callback ping"}

    print("Authorization Code:", code)
    print("Shop ID:", shop_id)

    try:
        # 1. แลก token จริงจาก Shopee
        token_response = get_token(code, shop_id)

        # 2. บันทึก token ลง Google Sheet
        save_token(
            platform="shopee",
            account_id=shop_id,
            access_token=token_response["access_token"],
            refresh_token=token_response["refresh_token"],
            expires_in=token_response.get("expire_in"),
            refresh_expires_in=token_response.get("refresh_expires_in")
        )

        return {"message": "✅ Token saved successfully."}

    except ValueError as e:
        return {
            "error": "Invalid authorization code. Please try again.",
            "details": str(e)
        }

async def shopee_check_shop(shop_id: int):
    info = check_shop_type(shop_id)
    return info

@app.get("/shopee/shop_info")
async def shopee_shop_info(shop_id: int):
    shop_info = call_shopee_api_auto("/shop/get_shop_info", shop_id)
    return shop_info

@app.get("/shopee/products")
async def shopee_products(shop_id: int, page_size: int = 10, page: int = 1):
    offset = (page - 1) * page_size
    products = call_shopee_api_auto("/product/get_item_list", shop_id, params={
        "pagination_offset": offset,
        "pagination_entries_per_page": page_size
    })
    return products

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