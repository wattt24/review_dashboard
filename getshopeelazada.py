# getshopeelazada.py
# getshopeelazada.py
from fastapi import FastAPI, Request
from fastapi.responses import Response
from services.test_auth import get_token, save_token,call_shopee_api
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from api.facebook_graph_api import get_page_tokens, get_page_posts, get_comments, get_page_insights, get_post_insights
app = FastAPI(title="Fujika Dashboard API")

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Service is running"}

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

@app.get("/")
async def root():
    return {"message": "Service is running"}

@app.get("/shopee/callback")
async def shopee_callback(code: str, shop_id: int):
    # 1. Log ค่าที่ได้
    print("Authorization Code:", code)
    print("Shop ID:", shop_id)

    # 2. เรียก get_token เพื่อแลก access_token (Sandbox จะ mock token)
    token_response = get_token(code, shop_id)

    # 3. ทดสอบเรียก API ของ Shopee (เช่น /shop/get)
    resp = call_shopee_api(
        path="/api/v2/shop/get",
        shop_id=shop_id,
        access_token=token_response["access_token"]
    )
    print("==== DEBUG /api/v2/shop/get ====")
    print(resp)

    # 4. ส่งผลลัพธ์กลับ browser
    return {
        "message": "Shopee callback received",
        "code": code,
        "shop_id": shop_id,
        "token_response": token_response,
        "shop_info": resp
    }


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

# @app.get("/shopee/callback")
# async def shopee_callback(shop_id: str, code: str | None = Query(default=None)):
#     try:
#         if code is None:
#             return {"status": "error", "detail": "Missing code parameter"}

#         tokens = get_token(code, shop_id)

#         if not tokens:
#             return {"status": "error", "detail": "get_token returned None"}

#         if "access_token" in tokens:
#             save_token(
#                 shop_id,
#                 tokens["access_token"],
#                 tokens["refresh_token"],
#                 tokens["expires_in"],
#                 tokens["refresh_expires_in"]
#             )
#             return {"status": "ok", "shop_id": shop_id}
#         else:
#             return {"status": "error", "detail": tokens}

#     except Exception as e:
#         import traceback
#         return {
#             "status": "exception",
#             "error": str(e),
#             "trace": traceback.format_exc()
#         }

