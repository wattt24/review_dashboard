from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/auth/shopee/callback")
async def shopee_callback(request: Request):
    code = request.query_params.get("code")
    # ดำเนินการแลก access token ฯลฯ
    return {"platform": "shopee", "code": code}
