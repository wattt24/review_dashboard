#ge
from fastapi import FastAPI
from services.shopee_auth import get_token

app = FastAPI()
@app.get("/")
def home():
    return {"msg": "Shopee Backend is running"}


@app.get("/shopee/callback")
def shopee_callback(code: str, shop_id: int, main_account_id: int = None):
    """รับ code หลังจากร้าน authorize แล้ว"""
    token_data = get_token(code, shop_id)

    # --- เตรียมข้อมูล ---
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expire_in = token_data.get("expire_in")   # วินาที
    expired_at = datetime.now().timestamp() + expire_in

    # --- บันทึกลง Google Sheet ---
    try:
        # ถ้ามี shop_id อยู่แล้ว → update
        cell = sheet.find(str(shop_id))
        sheet.update_cell(cell.row, 2, access_token)
        sheet.update_cell(cell.row, 3, refresh_token)
        sheet.update_cell(cell.row, 4, str(expired_at))
        sheet.update_cell(cell.row, 5, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except gspread.exceptions.CellNotFound:
        # ถ้าไม่มี → append row ใหม่
        sheet.append_row([
            str(shop_id),
            access_token,
            refresh_token,
            str(expired_at),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])

    return {
        "status": "success",
        "shop_id": shop_id,
        "token_data": token_data
    }
