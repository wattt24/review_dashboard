# getshopeelazada.py
# getshopeelazada.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from services.shopee_auth import get_token,call_shopee_api
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

    # 2. ถ้ามี access_token → เรียก shop/get
    shop_info = {}
    if "access_token" in token_response:
        shop_info = call_shopee_api(
            path="/api/v2/shop/get",
            shop_id=shop_id,
            access_token=token_response["access_token"]
        )

    return {
        "message": "Shopee callback received",
        "code": code,
        "shop_id": shop_id,
        "token_response": token_response,
        "shop_info": shop_info
    }

# @app.get("/shopee/callback")
# async def shopee_callback(code: str, shop_id: int):
#     # 1. Log ค่าที่ได้
#     print("Authorization Code:", code)
#     print("Shop ID:", shop_id)

#     # 2. เรียก get_token เพื่อแลก access_token
#     token_response = get_token(code, shop_id)

#     return {
#         "message": "Shopee callback received",
#         "code": code,
#         "shop_id": shop_id,
#         "token_response": token_response
#     }

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

