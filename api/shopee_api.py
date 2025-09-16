# api/shopee_api.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from services.shopee_auth import call_shopee_api_auto

# ------------------ Google Sheet setup ------------------
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

sheet = client.open("ShopList").worksheet("Shopee")  # ชื่อ Sheet ของ Shopee
shop_ids = sheet.col_values(2)  # สมมติ Shop_ID อยู่คอลัมน์ B (index=2)

# เอา shop_id แรกมาใช้งาน
shop_id = int(shop_ids[1])  # skip header
print("Using Shop ID:", shop_id)

# ------------------ ดึงข้อมูลร้าน ------------------
shop_info = call_shopee_api_auto("/shop/get_shop_info", shop_id)
print("Shop ID:", shop_info.get('shop_id'))
print("Shop Name:", shop_info.get('shop_name'))
print("Shop Logo:", shop_info.get('shop_logo'))

# ------------------ ดึงสินค้าของร้าน ------------------
params = {
    "pagination_offset": 0,
    "pagination_entries_per_page": 50,
    "item_status": "NORMAL"
}
products = call_shopee_api_auto("/product/get_item_list", shop_id, params=params)

for item in products.get('items', []):
    print("Item ID:", item.get('item_id'))
    print("Name:", item.get('name'))
    print("Price:", item.get('price'))
    print("Stock:", item.get('stock'))
    print("Image:", item.get('image'))
    print("---")
