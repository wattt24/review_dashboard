
# getshopeelazada.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from services.shopee_auth import get_token,call_shopee_api,call_shopee_api_auto
from services.lazada_auth import get_lazada_token, call_lazada_api
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from utils.token_manager import *
from api.facebook_graph_api import get_page_tokens, get_page_posts, get_comments, get_page_insights
app = FastAPI(title="Fujika Dashboard API")

@app.get("/")
async def root():
    return {"message": "Service is running"}
@app.api_route("/shopee/callback", methods=["GET", "HEAD"])
async def shopee_callback(code: str = None, shop_id: int = None):
    if not code or not shop_id:
        return {"message": "Shopee callback ping"}

    print("Authorization Code:", code)
    print("Shop ID:", shop_id)

    # 1. แลก token จริงจาก Shopee
    token_response = get_token(code, shop_id)

    # 2. บันทึก token ลง Google Sheet
    save_token(
        platform="shopee",
        account_id=shop_id,
        access_token=token_response["access_token"],
        refresh_token=token_response["refresh_token"],
        expires_in=token_response.get("expire_in"),             # Shopee ใช้ expire_in
        refresh_expires_in=token_response.get("refresh_expires_in")
    )

    # 3. ลองเรียก shop_info ด้วย auto-refresh token
    try:
        shop_info = call_shopee_api_auto("/api/v2/shop/get_shop_info", shop_id)
        print("shop_info:", shop_info)
    except Exception as e:
        print("Error calling Shopee API:", e)
        shop_info = {"error": str(e)}

    # ✅ ไม่ว่าจะ error หรือไม่ ต้อง return ออกไป
    return JSONResponse({
        "message": "Shopee callback received and token saved",
        "shop_id": shop_id,
        "token_response": token_response,
        "shop_info": shop_info
    })


@app.get("/shopee/shop_info")
async def shopee_shop_info(shop_id: int):
    return call_shopee_api_auto("/api/v2/shop/get_shop_info", shop_id)

@app.get("/shopee/products")
async def shopee_products(shop_id: int, page_size: int = 10):
    return call_shopee_api_auto(
        "/api/v2/product/get_item_list",
        shop_id,
        params={"page_size": page_size}
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
# ----- Facebook routes -----
@app.get("/api/facebook/pages")
async def pages(user_token: str = Query(...)):
    return JSONResponse(content=get_page_tokens(user_token))

@app.get("/api/facebook/posts/{page_id}")
async def posts(page_id: str, page_token: str = Query(...)):
    return JSONResponse(content=get_page_posts(page_id, page_token))

@app.get("/api/facebook/comments/{post_id}")
async def comments(post_id: str, page_token: str = Query(...)):
    return JSONResponse(content=get_comments(post_id, page_token))

@app.get("/api/facebook/insights/page/{page_id}")
async def page_insights(page_id: str, page_token: str = Query(...)):
    return JSONResponse(content=get_page_insights(page_id, page_token))

