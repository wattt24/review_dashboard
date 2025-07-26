#หลักการ FastAPI backend ไป deploy บน Render แล้วได้ URL ที่สามารถเชื่อมต่อได้
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.get("/shopee/callback")
async def shopee_callback(request: Request):
    # ดึงค่า code และ shop_id จาก query parameters
    code = request.query_params.get("code")
    shop_id = request.query_params.get("shop_id")

    if not code or not shop_id:
        raise HTTPException(status_code=400, detail="Missing code or shop_id")

    # แค่แสดงค่าที่รับมา (สามารถต่อยอดแลก token ได้ในขั้นตอนถัดไป)
    return {
        "message": "Received callback from Shopee",
        "code": code,
        "shop_id": shop_id
    }
@app.get("/lazada/callback")
async def lazada_callback(request: Request):
    code = request.query_params.get("code")
    lazada_id = request.query_params.get("lazada_id")  # Lazada อาจส่ง user_id หรือ partner_id ตั้งชื่อให้เ=lazada_id

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    # TODO: ต่อยอดด้วยการแลก token Lazada ที่นี่
    return {"message": "Received Lazada callback",
            "code": code, 
            "user_id": lazada_id}