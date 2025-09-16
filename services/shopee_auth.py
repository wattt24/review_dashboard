import gspread
from oauth2client.service_account import ServiceAccountCredentials
from services.shopee_auth import call_shopee_api_auto

# ------------------ Google Sheet setup ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open("ShopList").worksheet("Shopee")  # ชื่อ Sheet ของ Shopee
shop_ids = sheet.col_values(2)  # สมมติ Shop_ID อยู่คอลัมน์ B (index=2)

# เอา shop_id แรกมาใช้งาน (skip header)
shop_id = int(shop_ids[1])

# ------------------ ดึงข้อมูลร้าน ------------------
shop_info = call_shopee_api_auto('shop/get_shop_info', {"shop_id": shop_id})
shop_data = {
    "shop_id": shop_info.get("shop_id"),
    "shop_name": shop_info.get("shop_name"),
    "shop_logo": shop_info.get("shop_logo")
}

# ------------------ ดึงสินค้าของร้าน ------------------
items_response = call_shopee_api_auto('items/get', {
    "shop_id": shop_id,
    "pagination_offset": 0,
    "pagination_entries_per_page": 50
})

item_list = []
for item in items_response.get("item_list", []):
    item_list.append({
        "item_id": item.get("item_id"),
        "name": item.get("name"),
        "price": item.get("price"),
        "stock": item.get("stock"),
        "image": item.get("image")
    })

# ตอนนี้ shop_data กับ item_list สามารถเอาไปใช้ใน Streamlit หรือส่วนอื่นๆ ได้เลย
